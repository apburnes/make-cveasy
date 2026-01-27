"""Tests for token metering service."""

import pytest
import logging
from unittest.mock import Mock, patch, PropertyMock
from io import StringIO

from cveasy.services.metering_service import (
    TokenCounter,
    TokenExtractor,
    TokenMeteringService,
    TokenUsage,
)
from cveasy.ai.metered_provider import MeteredAIProvider
from cveasy.ai.providers import AIProvider


class TestTokenCounter:
    """Tests for TokenCounter class."""

    def test_estimate_tokens_openai_with_tiktoken(self):
        """Test token estimation for OpenAI models using tiktoken."""
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_encoding = Mock()
            mock_encoding.encode.return_value = [1, 2, 3, 4, 5]  # 5 tokens
            mock_get_encoding.return_value = mock_encoding

            count = TokenCounter.estimate_tokens("test text", "gpt-4", "openai")
            assert count == 5
            mock_get_encoding.assert_called_once_with("cl100k_base")

    def test_estimate_tokens_openai_fallback(self):
        """Test token estimation fallback when tiktoken fails."""
        with patch("tiktoken.get_encoding", side_effect=ImportError("No module")):
            count = TokenCounter.estimate_tokens("test text", "gpt-4", "openai")
            # Fallback: ~4 chars per token, so "test text" (9 chars) = ~2 tokens
            assert count == 2

    def test_estimate_tokens_anthropic(self):
        """Test token estimation for Anthropic models."""
        count = TokenCounter.estimate_tokens("test text here", "claude-3-haiku", "anthropic")
        # Anthropic: ~4 chars per token, so 14 chars = ~3 tokens
        assert count == 3

    def test_estimate_tokens_openrouter(self):
        """Test token estimation for OpenRouter models."""
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_encoding = Mock()
            mock_encoding.encode.return_value = [1, 2, 3]  # 3 tokens
            mock_get_encoding.return_value = mock_encoding

            count = TokenCounter.estimate_tokens("test", "openai/gpt-4", "openrouter")
            assert count == 3

    def test_estimate_tokens_empty_text(self):
        """Test token estimation with empty text."""
        count = TokenCounter.estimate_tokens("", "gpt-4", "openai")
        assert count == 0

    def test_get_encoding_for_model_gpt4(self):
        """Test encoding selection for GPT-4 models."""
        assert TokenCounter._get_encoding_for_model("gpt-4") == "cl100k_base"
        assert TokenCounter._get_encoding_for_model("gpt-4-turbo") == "cl100k_base"
        assert TokenCounter._get_encoding_for_model("GPT4") == "cl100k_base"

    def test_get_encoding_for_model_gpt35(self):
        """Test encoding selection for GPT-3.5 models."""
        assert TokenCounter._get_encoding_for_model("gpt-3.5-turbo") == "cl100k_base"
        assert TokenCounter._get_encoding_for_model("gpt-35-turbo") == "cl100k_base"

    def test_get_encoding_for_model_gpt3(self):
        """Test encoding selection for GPT-3 models."""
        assert TokenCounter._get_encoding_for_model("gpt-3") == "p50k_base"
        assert TokenCounter._get_encoding_for_model("text-davinci-003") == "p50k_base"

    def test_get_encoding_for_model_unknown(self):
        """Test encoding selection for unknown models defaults to cl100k_base."""
        assert TokenCounter._get_encoding_for_model("unknown-model") == "cl100k_base"

    def test_estimate_prompt_tokens_with_system_prompt(self):
        """Test prompt token estimation with system prompt."""
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_encoding = Mock()
            # Mock encoding to return different token counts
            def encode_side_effect(text):
                return list(range(len(text.split())))  # One token per word

            mock_encoding.encode.side_effect = encode_side_effect
            mock_get_encoding.return_value = mock_encoding

            count = TokenCounter.estimate_prompt_tokens(
                "user prompt", "system prompt", "gpt-4", "openai"
            )
            # Should include both prompts plus message overhead
            assert count > 0

    def test_estimate_prompt_tokens_without_system_prompt(self):
        """Test prompt token estimation without system prompt."""
        with patch("tiktoken.get_encoding") as mock_get_encoding:
            mock_encoding = Mock()
            mock_encoding.encode.return_value = [1, 2, 3]  # 3 tokens
            mock_get_encoding.return_value = mock_encoding

            count = TokenCounter.estimate_prompt_tokens("user prompt", None, "gpt-4", "openai")
            # Should include prompt tokens plus message overhead
            assert count >= 3


class TestTokenExtractor:
    """Tests for TokenExtractor class."""

    def test_extract_openai_tokens(self):
        """Test token extraction from OpenAI response."""
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30

        mock_response = Mock()
        mock_response.usage = mock_usage

        result = TokenExtractor.extract_tokens(mock_response, "openai")
        assert result["prompt_tokens"] == 10
        assert result["completion_tokens"] == 20
        assert result["total_tokens"] == 30

    def test_extract_openai_tokens_missing_usage(self):
        """Test token extraction when usage is missing."""
        mock_response = Mock()
        mock_response.usage = None

        result = TokenExtractor.extract_tokens(mock_response, "openai")
        assert result["prompt_tokens"] is None
        assert result["completion_tokens"] is None
        assert result["total_tokens"] is None

    def test_extract_anthropic_tokens(self):
        """Test token extraction from Anthropic response."""
        mock_usage = Mock()
        mock_usage.input_tokens = 15
        mock_usage.output_tokens = 25

        mock_response = Mock()
        mock_response.usage = mock_usage

        result = TokenExtractor.extract_tokens(mock_response, "anthropic")
        assert result["prompt_tokens"] == 15
        assert result["completion_tokens"] == 25
        assert result["total_tokens"] == 40

    def test_extract_anthropic_tokens_partial(self):
        """Test token extraction from Anthropic response with partial data."""
        mock_usage = Mock()
        mock_usage.input_tokens = 15
        mock_usage.output_tokens = None

        mock_response = Mock()
        mock_response.usage = mock_usage

        result = TokenExtractor.extract_tokens(mock_response, "anthropic")
        assert result["prompt_tokens"] == 15
        assert result["completion_tokens"] is None
        assert result["total_tokens"] is None

    def test_extract_tokens_unknown_provider(self):
        """Test token extraction for unknown provider."""
        mock_response = Mock()
        result = TokenExtractor.extract_tokens(mock_response, "unknown")
        assert result["prompt_tokens"] is None
        assert result["completion_tokens"] is None
        assert result["total_tokens"] is None

    def test_extract_tokens_exception_handling(self):
        """Test token extraction handles exceptions gracefully."""
        mock_response = Mock()
        # Cause an exception when accessing usage
        mock_response.usage = Mock()
        type(mock_response.usage).prompt_tokens = PropertyMock(side_effect=Exception("Test exception"))

        result = TokenExtractor.extract_tokens(mock_response, "openai")
        # Should return None values instead of raising
        assert result["prompt_tokens"] is None


class TestTokenMeteringService:
    """Tests for TokenMeteringService class."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock AI provider."""
        provider = Mock(spec=AIProvider)
        provider.generate.return_value = "Generated response"
        provider.model = "gpt-4"
        provider._last_response = None
        return provider

    @pytest.fixture
    def mock_logger(self):
        """Create a mock logger."""
        logger = logging.getLogger("test_metering")
        logger.setLevel(logging.INFO)
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        logger.addHandler(handler)
        return logger, log_capture

    def test_meter_call_with_token_extraction(self, mock_provider, mock_logger):
        """Test metering a call with successful token extraction."""
        logger, log_capture = mock_logger

        # Setup mock response with usage
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30

        mock_response = Mock()
        mock_response.usage = mock_usage
        mock_provider._last_response = mock_response

        service = TokenMeteringService(logger_instance=logger)

        with patch.object(service.token_counter, "estimate_prompt_tokens", return_value=12):
            text, usage = service.meter_call(
                mock_provider, "openai", "gpt-4", "test prompt", None, "test_operation"
            )

        assert text == "Generated response"
        assert usage.estimated_prompt_tokens == 12
        assert usage.actual_prompt_tokens == 10
        assert usage.actual_completion_tokens == 20
        assert usage.total_tokens == 30

        # Check that logging occurred
        log_output = log_capture.getvalue()
        assert "AI Token Usage" in log_output
        assert "openai" in log_output
        assert "gpt-4" in log_output

    def test_meter_call_without_token_extraction(self, mock_provider, mock_logger):
        """Test metering a call without token extraction."""
        logger, log_capture = mock_logger

        mock_provider._last_response = None

        service = TokenMeteringService(logger_instance=logger)

        with patch.object(service.token_counter, "estimate_prompt_tokens", return_value=15):
            text, usage = service.meter_call(
                mock_provider, "anthropic", "claude-3-haiku", "test prompt", "system prompt"
            )

        assert text == "Generated response"
        assert usage.estimated_prompt_tokens == 15
        assert usage.actual_prompt_tokens is None
        assert usage.actual_completion_tokens is None
        assert usage.total_tokens is None

    def test_meter_call_logs_duration(self, mock_provider, mock_logger):
        """Test that metering logs call duration."""
        logger, log_capture = mock_logger

        service = TokenMeteringService(logger_instance=logger)

        # Use a callable that returns values in sequence but handles extra calls gracefully
        call_count = [0]  # Use list to allow modification in nested function
        def time_side_effect():
            call_count[0] += 1
            if call_count[0] == 1:
                return 0.0
            elif call_count[0] == 2:
                return 0.5
            else:
                # If called more times than expected, return a reasonable value
                return 1.0

        with patch.object(service.token_counter, "estimate_prompt_tokens", return_value=10):
            with patch("time.time", side_effect=time_side_effect):
                service.meter_call(mock_provider, "openai", "gpt-4", "test", None)

        log_output = log_capture.getvalue()
        assert "Duration" in log_output

    def test_meter_call_with_operation_context(self, mock_provider, mock_logger):
        """Test metering with operation context."""
        logger, log_capture = mock_logger

        service = TokenMeteringService(logger_instance=logger)

        with patch.object(service.token_counter, "estimate_prompt_tokens", return_value=10):
            service.meter_call(
                mock_provider,
                "openai",
                "gpt-4",
                "test",
                None,
                operation_context="resume_generation",
            )

        log_output = log_capture.getvalue()
        assert "resume_generation" in log_output


class TestMeteredAIProvider:
    """Tests for MeteredAIProvider wrapper."""

    @pytest.fixture
    def mock_provider(self):
        """Create a mock AI provider."""
        provider = Mock(spec=AIProvider)
        provider.generate.return_value = "Generated text"
        provider.model = "gpt-4"
        provider._last_response = None
        return provider

    def test_metered_provider_wraps_generate(self, mock_provider):
        """Test that MeteredAIProvider wraps generate calls."""
        metered = MeteredAIProvider(mock_provider)
        MeteredAIProvider.reset_total_tokens()

        with patch("cveasy.services.metering_service.TokenMeteringService.meter_call") as mock_meter:
            token_usage = TokenUsage(estimated_prompt_tokens=10, actual_prompt_tokens=10, actual_completion_tokens=20, total_tokens=30)
            mock_meter.return_value = ("Generated text", token_usage)
            result = metered.generate("test prompt", "system prompt")

            assert result == "Generated text"
            mock_meter.assert_called_once()
            call_kwargs = mock_meter.call_args[1]
            assert call_kwargs["prompt"] == "test prompt"
            assert call_kwargs["system_prompt"] == "system prompt"
            # Verify tokens were accumulated
            assert MeteredAIProvider.get_total_tokens() == 30

    def test_metered_provider_detects_openai(self, mock_provider):
        """Test provider name detection for OpenAI."""
        mock_provider.__class__.__name__ = "OpenAIProvider"
        metered = MeteredAIProvider(mock_provider)

        assert metered._get_provider_name() == "openai"

    def test_metered_provider_detects_anthropic(self, mock_provider):
        """Test provider name detection for Anthropic."""
        mock_provider.__class__.__name__ = "AnthropicProvider"
        metered = MeteredAIProvider(mock_provider)

        assert metered._get_provider_name() == "anthropic"

    def test_metered_provider_detects_openrouter(self, mock_provider):
        """Test provider name detection for OpenRouter."""
        mock_provider.__class__.__name__ = "OpenRouterProvider"
        metered = MeteredAIProvider(mock_provider)

        assert metered._get_provider_name() == "openrouter"

    def test_metered_provider_gets_model_name(self, mock_provider):
        """Test model name extraction."""
        mock_provider.model = "gpt-4-turbo"
        metered = MeteredAIProvider(mock_provider)

        assert metered._get_model_name() == "gpt-4-turbo"

    def test_metered_provider_operation_context(self, mock_provider):
        """Test operation context is passed to metering service."""
        metered = MeteredAIProvider(mock_provider, operation_context="resume_check")
        MeteredAIProvider.reset_total_tokens()

        with patch("cveasy.services.metering_service.TokenMeteringService.meter_call") as mock_meter:
            token_usage = TokenUsage(estimated_prompt_tokens=15)
            mock_meter.return_value = ("Generated text", token_usage)
            metered.generate("test")

            call_kwargs = mock_meter.call_args[1]
            assert call_kwargs["operation_context"] == "resume_check"
            # Verify tokens were accumulated
            assert MeteredAIProvider.get_total_tokens() == 15

    def test_metered_provider_implements_ai_provider(self, mock_provider):
        """Test that MeteredAIProvider implements AIProvider interface."""
        metered = MeteredAIProvider(mock_provider)
        assert isinstance(metered, AIProvider)

    def test_metered_provider_token_tracking(self, mock_provider):
        """Test that MeteredAIProvider tracks total tokens."""
        MeteredAIProvider.reset_total_tokens()
        metered = MeteredAIProvider(mock_provider)

        with patch("cveasy.services.metering_service.TokenMeteringService.meter_call") as mock_meter:
            token_usage1 = TokenUsage(estimated_prompt_tokens=10, total_tokens=25)
            token_usage2 = TokenUsage(estimated_prompt_tokens=15, total_tokens=35)
            mock_meter.side_effect = [
                ("Generated text 1", token_usage1),
                ("Generated text 2", token_usage2),
            ]

            result1 = metered.generate("test 1")
            result2 = metered.generate("test 2")

            assert result1 == "Generated text 1"
            assert result2 == "Generated text 2"
            assert MeteredAIProvider.get_total_tokens() == 60  # 25 + 35

    def test_metered_provider_reset_total_tokens(self, mock_provider):
        """Test that reset_total_tokens resets the counter."""
        MeteredAIProvider.reset_total_tokens()
        metered = MeteredAIProvider(mock_provider)

        with patch("cveasy.services.metering_service.TokenMeteringService.meter_call") as mock_meter:
            token_usage = TokenUsage(estimated_prompt_tokens=10, total_tokens=30)
            mock_meter.return_value = ("Generated text", token_usage)

            metered.generate("test")
            assert MeteredAIProvider.get_total_tokens() == 30

            MeteredAIProvider.reset_total_tokens()
            assert MeteredAIProvider.get_total_tokens() == 0
