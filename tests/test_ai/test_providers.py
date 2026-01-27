"""Tests for AI providers."""

import os
from unittest.mock import patch


def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "test-key"}):
        with patch("openai.OpenAI") as mock_openai:
            from cveasy.ai.providers import OpenAIProvider

            provider = OpenAIProvider(api_key="test-key")

            assert provider.api_key == "test-key"
            mock_openai.assert_called_once_with(api_key="test-key")


def test_openai_provider_uses_unified_api_key():
    """Test OpenAI provider uses CVEASY_API_KEY from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "env-test-key"}):
        with patch("openai.OpenAI") as mock_openai:
            from cveasy.ai.providers import OpenAIProvider

            provider = OpenAIProvider()

            assert provider.api_key == "env-test-key"
            mock_openai.assert_called_once_with(api_key="env-test-key")


def test_openai_provider_uses_unified_model():
    """Test OpenAI provider uses CVEASY_MODEL from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "test-key", "CVEASY_MODEL": "gpt-4-turbo"}):
        with patch("openai.OpenAI") as _:
            from cveasy.ai.providers import OpenAIProvider

            provider = OpenAIProvider()

            assert provider.model == "gpt-4-turbo"


def test_anthropic_provider_initialization():
    """Test Anthropic provider initialization."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "test-key"}):
        with patch("anthropic.Anthropic") as mock_anthropic:
            from cveasy.ai.providers import AnthropicProvider

            provider = AnthropicProvider(api_key="test-key")

            assert provider.api_key == "test-key"
            mock_anthropic.assert_called_once_with(api_key="test-key")


def test_anthropic_provider_uses_unified_api_key():
    """Test Anthropic provider uses CVEASY_API_KEY from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "env-test-key"}):
        with patch("anthropic.Anthropic") as mock_anthropic:
            from cveasy.ai.providers import AnthropicProvider

            provider = AnthropicProvider()

            assert provider.api_key == "env-test-key"
            mock_anthropic.assert_called_once_with(api_key="env-test-key")


def test_anthropic_provider_uses_unified_model():
    """Test Anthropic provider uses CVEASY_MODEL from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "test-key", "CVEASY_MODEL": "claude-3-opus"}):
        with patch("anthropic.Anthropic") as _:
            from cveasy.ai.providers import AnthropicProvider

            provider = AnthropicProvider()

            assert provider.model == "claude-3-opus"


def test_anthropic_provider_uses_unified_max_tokens():
    """Test Anthropic provider uses CVEASY_MAX_TOKENS from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "test-key", "CVEASY_MAX_TOKENS": "4096"}):
        with patch("anthropic.Anthropic") as _:
            from cveasy.ai.providers import AnthropicProvider

            provider = AnthropicProvider()

            assert provider.max_tokens == 4096


def test_openrouter_provider_uses_unified_api_key():
    """Test OpenRouter provider uses CVEASY_API_KEY from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "env-test-key"}):
        with patch("openai.OpenAI") as mock_openai:
            from cveasy.ai.providers import OpenRouterProvider

            provider = OpenRouterProvider()

            assert provider.api_key == "env-test-key"
            # Check that base_url is set correctly
            mock_openai.assert_called_once_with(
                api_key="env-test-key",
                base_url="https://openrouter.ai/api/v1",
            )


def test_openrouter_provider_uses_unified_model():
    """Test OpenRouter provider uses CVEASY_MODEL from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "test-key", "CVEASY_MODEL": "anthropic/claude-3-opus"}):
        with patch("openai.OpenAI") as _:
            from cveasy.ai.providers import OpenRouterProvider

            provider = OpenRouterProvider()

            assert provider.model == "anthropic/claude-3-opus"
