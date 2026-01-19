"""Metered AI provider wrapper for token tracking."""

from typing import Optional

from cveasy.ai.providers import AIProvider
from cveasy.services.metering_service import TokenMeteringService


class MeteredAIProvider(AIProvider):
    """Wrapper around AIProvider that adds token metering."""

    # Class-level accumulators for tokens across all instances
    _total_tokens_used: int = 0
    _input_tokens_used: int = 0
    _output_tokens_used: int = 0

    def __init__(self, provider: AIProvider, operation_context: Optional[str] = None):
        """
        Initialize metered provider.

        Args:
            provider: The underlying AI provider to wrap
            operation_context: Optional context for operations (e.g., "resume_generation")
        """
        self.provider = provider
        self.operation_context = operation_context
        self.metering_service = TokenMeteringService()

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using the wrapped provider with token metering.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text
        """
        # Get provider name and model
        provider_name = self._get_provider_name()
        model = self._get_model_name()

        # Use metering service to track the call
        generated_text, token_usage = self.metering_service.meter_call(
            provider_instance=self.provider,
            provider_name=provider_name,
            model=model,
            prompt=prompt,
            system_prompt=system_prompt,
            operation_context=self.operation_context,
        )

        # Accumulate input and output tokens separately, then calculate total
        try:
            # Track input tokens
            input_tokens = None
            if token_usage.input_tokens is not None and isinstance(token_usage.input_tokens, int):
                input_tokens = token_usage.input_tokens
            elif token_usage.actual_prompt_tokens is not None and isinstance(token_usage.actual_prompt_tokens, int):
                input_tokens = token_usage.actual_prompt_tokens
            elif isinstance(token_usage.estimated_prompt_tokens, int):
                input_tokens = token_usage.estimated_prompt_tokens

            # Track output tokens
            output_tokens = None
            if token_usage.output_tokens is not None and isinstance(token_usage.output_tokens, int):
                output_tokens = token_usage.output_tokens
            elif token_usage.actual_completion_tokens is not None and isinstance(token_usage.actual_completion_tokens, int):
                output_tokens = token_usage.actual_completion_tokens

            # Accumulate tokens
            if input_tokens is not None:
                MeteredAIProvider._input_tokens_used += input_tokens
            if output_tokens is not None:
                MeteredAIProvider._output_tokens_used += output_tokens

            # Calculate total (prefer actual total, otherwise sum of input + output)
            if token_usage.total_tokens is not None and isinstance(token_usage.total_tokens, int):
                MeteredAIProvider._total_tokens_used += token_usage.total_tokens
            elif input_tokens is not None and output_tokens is not None:
                MeteredAIProvider._total_tokens_used += (input_tokens + output_tokens)
            elif input_tokens is not None:
                # If we only have input tokens, use that as total estimate
                MeteredAIProvider._total_tokens_used += input_tokens
        except (TypeError, AttributeError):
            # Handle cases where token_usage might be a mock or have unexpected types
            # Try to use estimated as fallback
            try:
                if isinstance(token_usage.estimated_prompt_tokens, int):
                    MeteredAIProvider._input_tokens_used += token_usage.estimated_prompt_tokens
                    MeteredAIProvider._total_tokens_used += token_usage.estimated_prompt_tokens
            except (TypeError, AttributeError):
                pass  # Skip accumulation if we can't determine token count

        return generated_text

    def _get_provider_name(self) -> str:
        """Get provider name from the wrapped provider."""
        class_name = self.provider.__class__.__name__
        if "OpenAI" in class_name:
            return "openai"
        elif "Anthropic" in class_name:
            return "anthropic"
        elif "OpenRouter" in class_name:
            return "openrouter"
        else:
            return "unknown"

    def _get_model_name(self) -> str:
        """Get model name from the wrapped provider."""
        if hasattr(self.provider, "model"):
            return self.provider.model
        return "unknown"

    @classmethod
    def get_total_tokens(cls) -> int:
        """
        Get total tokens used across all MeteredAIProvider instances.

        Returns:
            Total tokens used
        """
        return cls._total_tokens_used

    @classmethod
    def get_input_tokens(cls) -> int:
        """
        Get total input tokens used across all MeteredAIProvider instances.

        Returns:
            Total input tokens used
        """
        return cls._input_tokens_used

    @classmethod
    def get_output_tokens(cls) -> int:
        """
        Get total output tokens used across all MeteredAIProvider instances.

        Returns:
            Total output tokens used
        """
        return cls._output_tokens_used

    @classmethod
    def reset_total_tokens(cls) -> None:
        """Reset all token counters."""
        cls._total_tokens_used = 0
        cls._input_tokens_used = 0
        cls._output_tokens_used = 0
