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

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenAI provider."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

        self.api_key = api_key or get_openai_api_key()
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using OpenAI."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content


class AnthropicProvider(AIProvider):
    """Anthropic API provider."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize Anthropic provider."""
        try:
            import anthropic
        except ImportError:
            raise ImportError("anthropic package is required. Install with: pip install anthropic")

        self.api_key = api_key or get_anthropic_api_key()
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")

        self.client = anthropic.Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text using Anthropic."""
        messages = [{"role": "user", "content": prompt}]

        response = self.client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            system=system_prompt or "",
            messages=messages,
        )

        return response.content[0].text


class OpenRouterProvider(AIProvider):
    """OpenRouter API provider."""

    def __init__(self, api_key: Optional[str] = None, model: str = "openai/gpt-4"):
        """Initialize OpenRouter provider."""
        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError("openai package is required. Install with: pip install openai")

        self.api_key = api_key or get_openrouter_api_key()
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is required")

        self.model = model
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

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content


def get_ai_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get AI provider instance.

    Args:
        provider_name: Provider name (openai, anthropic, openrouter). If None, uses config.

    Returns:
        AIProvider instance
    """
    provider = provider_name or get_provider_config()

    if provider == "openai":
        return OpenAIProvider()
    elif provider == "anthropic":
        return AnthropicProvider()
    elif provider == "openrouter":
        return OpenRouterProvider()
    else:
        raise ValueError(f"Unknown AI provider: {provider}")
