"""AI provider abstraction layer."""

import logging
from abc import ABC, abstractmethod
from typing import Optional

from cveasy.config import (
    get_ai_provider as get_provider_config,
    get_cveasy_api_key,
    get_cveasy_model,
    get_cveasy_max_tokens,
)
from cveasy.exceptions import AIProviderError, ValidationError

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text using the AI provider.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt

        Returns:
            Generated text
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenAI provider."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ValidationError("openai package is required. Install with: pip install openai")

        self.api_key = api_key or get_cveasy_api_key()
        if not self.api_key:
            raise ValidationError("CVEASY_API_KEY environment variable is required")

        self.client = OpenAI(api_key=self.api_key)
        # Use model from parameter, env var, or default to gpt-4
        self.model = model or get_cveasy_model() or "gpt-4"
        self._last_response = None
        logger.debug("OpenAI provider initialized (model=%s)", self.model)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI."""
        from openai import OpenAIError

        logger.debug("OpenAI generate called (prompt: %d chars)", len(prompt))
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            # Store response for token extraction
            self._last_response = response
            return response.choices[0].message.content
        except OpenAIError as e:
            raise AIProviderError(f"OpenAI API error: {e}") from e


class AnthropicProvider(AIProvider):
    """Anthropic API provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ):
        """Initialize Anthropic provider."""
        try:
            import anthropic
        except ImportError:
            raise ValidationError(
                "anthropic package is required. Install with: pip install anthropic"
            )

        self.api_key = api_key or get_cveasy_api_key()
        if not self.api_key:
            raise ValidationError("CVEASY_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        # Use model from env var, parameter, or default to a widely available model
        # Default to claude-3-haiku-20240307 which is the most widely available
        # Users can override with CVEASY_MODEL environment variable
        # Common models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
        self.model = model or get_cveasy_model() or "claude-3-haiku-20240307"
        self.max_tokens = max_tokens if max_tokens is not None else get_cveasy_max_tokens()
        self._last_response = None
        logger.debug("Anthropic provider initialized (model=%s, max_tokens=%d)", self.model, self.max_tokens)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Anthropic."""
        import anthropic as anthropic_sdk

        logger.debug("Anthropic generate called (prompt: %d chars)", len(prompt))
        messages = [{"role": "user", "content": prompt}]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt or "",
                messages=messages,
            )

            # Store response for token extraction
            self._last_response = response

            # Check if response was truncated (stop_reason indicates truncation)
            if response.stop_reason == "max_tokens":
                raise AIProviderError(
                    f"Response was truncated because it exceeded max_tokens ({self.max_tokens}). "
                    f"The response may be incomplete. "
                    f"To fix this, increase CVEASY_MAX_TOKENS environment variable (current: {self.max_tokens}). "
                    f"Note: Anthropic models have maximum token limits (typically 4096-8192 depending on model)."
                )

            return response.content[0].text
        except AIProviderError:
            # Re-raise AIProviderError (including our truncation error)
            raise
        except anthropic_sdk.APIError as e:
            error_msg = str(e)
            # Provide helpful error message for model not found
            if "404" in error_msg or "not_found" in error_msg.lower():
                raise ValidationError(
                    f"Anthropic model '{self.model}' not found or not available. "
                    f"Please check:\n"
                    f"1. The model name is correct (common models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307)\n"
                    f"2. Your API key has access to this model\n"
                    f"3. Set CVEASY_MODEL environment variable to a valid model name\n"
                    f"Original error: {error_msg}"
                ) from e
            # Check for max_tokens related errors
            if "max_tokens" in error_msg.lower() or "token" in error_msg.lower():
                raise AIProviderError(
                    f"Token limit error: {error_msg}. "
                    f"Current max_tokens setting: {self.max_tokens}. "
                    f"You can adjust this with CVEASY_MAX_TOKENS environment variable."
                ) from e
            raise AIProviderError(f"Anthropic API error: {e}") from e


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenRouter provider."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ValidationError("openai package is required. Install with: pip install openai")

        self.api_key = api_key or get_cveasy_api_key()
        if not self.api_key:
            raise ValidationError("CVEASY_API_KEY environment variable is required")

        # Use model from parameter, env var, or default to openai/gpt-4
        self.model = model or get_cveasy_model() or "openai/gpt-4"
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )
        self._last_response = None
        logger.debug("OpenRouter provider initialized (model=%s)", self.model)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenRouter."""
        from openai import OpenAIError

        logger.debug("OpenRouter generate called (prompt: %d chars)", len(prompt))
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
            )
            # Store response for token extraction
            self._last_response = response
            return response.choices[0].message.content
        except OpenAIError as e:
            raise AIProviderError(f"OpenRouter API error: {e}") from e


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get AI provider instance.

    Args:
        provider_name: Provider name (openai, anthropic, openrouter). If None, uses config.

    Returns:
        AIProvider instance
    """
    # Import here to avoid circular import
    from cveasy.ai.metered_provider import MeteredAIProvider

    provider = provider_name or get_provider_config()
    # Normalize to lowercase for case-insensitive matching
    provider = provider.lower().strip() if provider else "openai"

    try:
        base_provider = None
        if provider == "openai":
            base_provider = OpenAIProvider()
        elif provider == "anthropic":
            base_provider = AnthropicProvider()
        elif provider == "openrouter":
            base_provider = OpenRouterProvider()
        else:
            raise ValidationError(
                f"Unknown AI provider: {provider}. Valid options are: openai, anthropic, openrouter"
            )

        # Wrap provider with metering
        return MeteredAIProvider(base_provider)
    except (ValidationError, AIProviderError):
        # Re-raise validation and provider errors
        raise
    except (ImportError, OSError) as e:
        # Wrap dependency and system errors
        raise AIProviderError(f"Failed to initialize {provider} provider: {e}") from e
