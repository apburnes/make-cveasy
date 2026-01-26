"""Token metering service for monitoring AI provider usage."""

import logging
import time
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TokenUsage:
    """Token usage information."""

    estimated_prompt_tokens: int
    actual_prompt_tokens: Optional[int] = None
    actual_completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None

    @property
    def input_tokens(self) -> Optional[int]:
        """Get input tokens (alias for actual_prompt_tokens)."""
        return self.actual_prompt_tokens

    @property
    def output_tokens(self) -> Optional[int]:
        """Get output tokens (alias for actual_completion_tokens)."""
        return self.actual_completion_tokens


class TokenCounter:
    """Token counter for estimating tokens before API calls."""

    @staticmethod
    def estimate_tokens(text: str, model: str, provider: str) -> int:
        """
        Estimate token count for text based on model and provider.

        Args:
            text: Text to estimate tokens for
            model: Model name
            provider: Provider name (openai, anthropic, openrouter)

        Returns:
            Estimated token count
        """
        if not text:
            return 0

        # For OpenAI and OpenRouter models, use tiktoken
        if provider in ("openai", "openrouter"):
            try:
                import tiktoken

                # Map common model names to tiktoken encodings
                encoding_name = TokenCounter._get_encoding_for_model(model)
                encoding = tiktoken.get_encoding(encoding_name)
                return len(encoding.encode(text))
            except (ImportError, Exception) as e:
                logger.warning(f"Failed to use tiktoken for token estimation: {e}. Using fallback.")
                # Fallback: approximate 4 characters per token
                return len(text) // 4

        # For Anthropic, use approximate estimation
        # Anthropic models typically use ~4 characters per token
        elif provider == "anthropic":
            # Rough estimation: ~4 characters per token for Claude models
            return len(text) // 4

        # Fallback for unknown providers
        else:
            return len(text) // 4

    @staticmethod
    def _get_encoding_for_model(model: str) -> str:
        """
        Get tiktoken encoding name for a model.

        Args:
            model: Model name

        Returns:
            Encoding name for tiktoken
        """
        model_lower = model.lower()

        # GPT-4 and GPT-3.5 models
        if "gpt-4" in model_lower or "gpt4" in model_lower:
            return "cl100k_base"  # GPT-4 uses cl100k_base
        elif "gpt-3.5" in model_lower or "gpt-35" in model_lower or "gpt3.5" in model_lower:
            return "cl100k_base"  # GPT-3.5-turbo uses cl100k_base
        elif (
            "davinci" in model_lower
            or "curie" in model_lower
            or "babbage" in model_lower
            or "ada" in model_lower
        ):
            return "p50k_base"  # Older GPT-3 models (text-davinci, etc.) use p50k_base
        elif "gpt-3" in model_lower or "gpt3" in model_lower:
            return "p50k_base"  # Older GPT-3 models use p50k_base
        else:
            # Default to cl100k_base for unknown OpenAI models
            return "cl100k_base"

    @staticmethod
    def estimate_prompt_tokens(
        prompt: str, system_prompt: Optional[str], model: str, provider: str
    ) -> int:
        """
        Estimate total prompt tokens including system prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            model: Model name
            provider: Provider name

        Returns:
            Estimated total prompt tokens
        """
        total_text = prompt
        if system_prompt:
            total_text = system_prompt + "\n" + prompt

        # Add overhead for message formatting (approximately 4 tokens per message)
        message_overhead = 4
        if system_prompt:
            message_overhead += 4  # Extra overhead for system message

        return TokenCounter.estimate_tokens(total_text, model, provider) + message_overhead


class TokenExtractor:
    """Extract token usage from provider responses."""

    @staticmethod
    def extract_tokens(response: Any, provider: str) -> Dict[str, Optional[int]]:
        """
        Extract token usage from provider response.

        Args:
            response: Provider response object
            provider: Provider name (openai, anthropic, openrouter)

        Returns:
            Dictionary with prompt_tokens (input), completion_tokens (output), total_tokens,
            input_tokens, and output_tokens
        """
        if provider in ("openai", "openrouter"):
            return TokenExtractor._extract_openai_tokens(response)
        elif provider == "anthropic":
            return TokenExtractor._extract_anthropic_tokens(response)
        else:
            return {
                "prompt_tokens": None,
                "completion_tokens": None,
                "total_tokens": None,
                "input_tokens": None,
                "output_tokens": None,
            }

    @staticmethod
    def _extract_openai_tokens(response: Any) -> Dict[str, Optional[int]]:
        """Extract tokens from OpenAI/OpenRouter response."""
        try:
            if hasattr(response, "usage") and response.usage:
                usage = response.usage
                prompt_tokens = getattr(usage, "prompt_tokens", None)
                completion_tokens = getattr(usage, "completion_tokens", None)
                total_tokens = getattr(usage, "total_tokens", None)
                return {
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": total_tokens,
                    "input_tokens": prompt_tokens,  # Record input tokens explicitly
                    "output_tokens": completion_tokens,  # Record output tokens explicitly
                }
        except Exception as e:
            logger.warning(f"Failed to extract tokens from OpenAI response: {e}")

        return {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "input_tokens": None,
            "output_tokens": None,
        }

    @staticmethod
    def _extract_anthropic_tokens(response: Any) -> Dict[str, Optional[int]]:
        """Extract tokens from Anthropic response."""
        try:
            if hasattr(response, "usage") and response.usage:
                usage = response.usage
                input_tokens = getattr(usage, "input_tokens", None)
                output_tokens = getattr(usage, "output_tokens", None)
                total = None
                if input_tokens is not None and output_tokens is not None:
                    total = input_tokens + output_tokens

                return {
                    "prompt_tokens": input_tokens,  # Map to prompt_tokens for compatibility
                    "completion_tokens": output_tokens,  # Map to completion_tokens for compatibility
                    "total_tokens": total,
                    "input_tokens": input_tokens,  # Record input tokens explicitly
                    "output_tokens": output_tokens,  # Record output tokens explicitly
                }
        except Exception as e:
            logger.warning(f"Failed to extract tokens from Anthropic response: {e}")

        return {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "input_tokens": None,
            "output_tokens": None,
        }


class TokenMeteringService:
    """Service for metering AI provider token usage."""

    def __init__(self, logger_instance: Optional[logging.Logger] = None):
        """
        Initialize metering service.

        Args:
            logger_instance: Optional logger instance. Defaults to module logger.
        """
        self.logger = logger_instance or logger
        self.token_counter = TokenCounter()
        self.token_extractor = TokenExtractor()

    def meter_call(
        self,
        provider_instance: Any,
        provider_name: str,
        model: str,
        prompt: str,
        system_prompt: Optional[str],
        operation_context: Optional[str] = None,
    ) -> tuple[str, TokenUsage]:
        """
        Meter an AI provider call, estimating tokens before and extracting after.

        Args:
            provider_instance: The AI provider instance
            provider_name: Provider name (openai, anthropic, openrouter)
            model: Model name
            prompt: User prompt
            system_prompt: Optional system prompt
            operation_context: Optional context for the operation (e.g., "resume_generation")

        Returns:
            Tuple of (generated_text, TokenUsage)
        """
        start_time = time.time()

        # Estimate tokens before the call
        estimated_prompt_tokens = self.token_counter.estimate_prompt_tokens(
            prompt, system_prompt, model, provider_name
        )

        # Make the actual API call
        # We need to capture the raw response to extract tokens
        # Since providers return strings, we need to modify the approach
        # We'll need to modify providers to return both text and raw response
        # For now, we'll call generate and try to extract from a stored response
        generated_text = provider_instance.generate(prompt, system_prompt)

        duration = time.time() - start_time

        # Extract actual tokens from response
        # Note: This requires access to the raw response object
        # We'll need to modify providers to store the last response
        actual_tokens = {
            "prompt_tokens": None,
            "completion_tokens": None,
            "total_tokens": None,
            "input_tokens": None,
            "output_tokens": None,
        }

        # Try to get tokens from provider if it stores the last response
        if hasattr(provider_instance, "_last_response"):
            actual_tokens = self.token_extractor.extract_tokens(
                provider_instance._last_response, provider_name
            )

        # Record input and output tokens explicitly
        input_tokens = actual_tokens.get("input_tokens") or actual_tokens.get("prompt_tokens")
        output_tokens = actual_tokens.get("output_tokens") or actual_tokens.get("completion_tokens")

        token_usage = TokenUsage(
            estimated_prompt_tokens=estimated_prompt_tokens,
            actual_prompt_tokens=input_tokens,  # Record as input tokens
            actual_completion_tokens=output_tokens,  # Record as output tokens
            total_tokens=actual_tokens.get("total_tokens"),
        )

        # Log token usage
        self._log_token_usage(
            provider_name=provider_name,
            model=model,
            token_usage=token_usage,
            duration=duration,
            operation_context=operation_context,
        )

        return generated_text, token_usage

    def _log_token_usage(
        self,
        provider_name: str,
        model: str,
        token_usage: TokenUsage,
        duration: float,
        operation_context: Optional[str] = None,
    ) -> None:
        """
        Log token usage information.

        Args:
            provider_name: Provider name
            model: Model name
            token_usage: TokenUsage object
            duration: Call duration in seconds
            operation_context: Optional operation context
        """
        log_data = {
            "provider": provider_name,
            "model": model,
            "estimated_prompt_tokens": token_usage.estimated_prompt_tokens,
            "actual_prompt_tokens": token_usage.actual_prompt_tokens,
            "actual_completion_tokens": token_usage.actual_completion_tokens,
            "input_tokens": token_usage.input_tokens,  # Record input tokens
            "output_tokens": token_usage.output_tokens,  # Record output tokens
            "total_tokens": token_usage.total_tokens,
            "duration_seconds": round(duration, 3),
        }

        if operation_context:
            log_data["operation_context"] = operation_context

        # Log as structured information with input/output tokens explicitly recorded
        self.logger.info(
            f"AI Token Usage - Provider: {provider_name}, Model: {model}, "
            f"Estimated Prompt Tokens: {token_usage.estimated_prompt_tokens}, "
            f"Input Tokens: {token_usage.input_tokens}, "
            f"Output Tokens: {token_usage.output_tokens}, "
            f"Total Tokens: {token_usage.total_tokens}, "
            f"Duration: {duration:.3f}s"
            + (f", Context: {operation_context}" if operation_context else "")
        )
