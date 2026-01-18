"""AI provider abstraction layer."""

from abc import ABC, abstractmethod
from typing import Optional
import os

from cveasy.config import (
    get_ai_provider as get_provider_config,
    get_openai_api_key,
    get_anthropic_api_key,
    get_openrouter_api_key,
)
from cveasy.exceptions import AIProviderError, ValidationError


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
            raise ImportError("openai package is required. Install with: pip install openai")

        self.api_key = api_key or get_openai_api_key()
        if not self.api_key:
            raise ValidationError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=self.api_key)
        # Use model from parameter, env var, or default to gpt-4
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4")

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI."""
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
            return response.choices[0].message.content
        except Exception as e:
            raise AIProviderError(f"OpenAI API error: {e}") from e


class AnthropicProvider(AIProvider):
    """Anthropic API provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None, max_tokens: Optional[int] = None):
        """Initialize Anthropic provider."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")

        self.api_key = api_key or get_anthropic_api_key()
        if not self.api_key:
            raise ValidationError("ANTHROPIC_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=self.api_key)
        # Use model from env var, parameter, or default to a widely available model
        # Default to claude-3-haiku-20240307 which is the most widely available
        # Users can override with ANTHROPIC_MODEL environment variable
        # Common models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-3-haiku-20240307")
        # Use max_tokens from parameter, env var, or default to 8192 (higher for resume parsing)
        # Note: Model limits vary (claude-3-5-sonnet supports 8192, older models typically 4096)
        # If you get truncation errors, try setting ANTHROPIC_MAX_TOKENS to a lower value (4096) for older models
        # or ensure you're using a model that supports higher limits
        default_max_tokens = int(os.getenv("ANTHROPIC_MAX_TOKENS", "8192"))
        self.max_tokens = max_tokens if max_tokens is not None else default_max_tokens

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Anthropic."""
        messages = [{"role": "user", "content": prompt}]

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                system=system_prompt or "",
                messages=messages,
            )

            # Check if response was truncated (stop_reason indicates truncation)
            if response.stop_reason == "max_tokens":
                raise AIProviderError(
                    f"Response was truncated because it exceeded max_tokens ({self.max_tokens}). "
                    f"The response may be incomplete. "
                    f"To fix this, increase ANTHROPIC_MAX_TOKENS environment variable (current: {self.max_tokens}). "
                    f"Note: Anthropic models have maximum token limits (typically 4096-8192 depending on model)."
                )

            return response.content[0].text
        except AIProviderError:
            # Re-raise AIProviderError (including our truncation error)
            raise
        except Exception as e:
            error_msg = str(e)
            # Provide helpful error message for model not found
            if "404" in error_msg or "not_found" in error_msg.lower():
                raise ValidationError(
                    f"Anthropic model '{self.model}' not found or not available. "
                    f"Please check:\n"
                    f"1. The model name is correct (common models: claude-3-5-sonnet-20241022, claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307)\n"
                    f"2. Your API key has access to this model\n"
                    f"3. Set ANTHROPIC_MODEL environment variable to a valid model name\n"
                    f"Original error: {error_msg}"
                ) from e
            # Check for max_tokens related errors
            if "max_tokens" in error_msg.lower() or "token" in error_msg.lower():
                raise AIProviderError(
                    f"Token limit error: {error_msg}. "
                    f"Current max_tokens setting: {self.max_tokens}. "
                    f"You can adjust this with ANTHROPIC_MAX_TOKENS environment variable."
                ) from e
            raise AIProviderError(f"Anthropic API error: {e}") from e


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize OpenRouter provider."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

        self.api_key = api_key or get_openrouter_api_key()
        if not self.api_key:
            raise ValidationError("OPENROUTER_API_KEY environment variable is required")

        # Use model from parameter, env var, or default to openai/gpt-4
        self.model = model or os.getenv("OPENROUTER_MODEL", "openai/gpt-4")
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://openrouter.ai/api/v1",
        )

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenRouter."""
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
            return response.choices[0].message.content
        except Exception as e:
            raise AIProviderError(f"OpenRouter API error: {e}") from e


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get AI provider instance.

    Args:
        provider_name: Provider name (openai, anthropic, openrouter). If None, uses config.

    Returns:
        AIProvider instance
    """
    provider = provider_name or get_provider_config()
    # Normalize to lowercase for case-insensitive matching
    provider = provider.lower().strip() if provider else "openai"

    try:
        if provider == "openai":
            return OpenAIProvider()
        elif provider == "anthropic":
            return AnthropicProvider()
        elif provider == "openrouter":
            return OpenRouterProvider()
        else:
            raise ValidationError(f"Unknown AI provider: {provider}. Valid options are: openai, anthropic, openrouter")
    except (ValidationError, AIProviderError):
        # Re-raise validation and provider errors
        raise
    except Exception as e:
        # Wrap other exceptions
        raise AIProviderError(f"Failed to initialize {provider} provider: {e}") from e
