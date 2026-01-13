"""Tests for AI providers."""

import pytest
from unittest.mock import Mock, patch


def test_openai_provider_initialization():
    """Test OpenAI provider initialization."""
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        with patch("cveasy.ai.providers.OpenAI") as mock_openai:
            from cveasy.ai.providers import OpenAIProvider

            provider = OpenAIProvider(api_key="test-key")

            assert provider.api_key == "test-key"


def test_anthropic_provider_initialization():
    """Test Anthropic provider initialization."""
    with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
        with patch("cveasy.ai.providers.anthropic") as mock_anthropic:
            from cveasy.ai.providers import AnthropicProvider

            provider = AnthropicProvider(api_key="test-key")

            assert provider.api_key == "test-key"
