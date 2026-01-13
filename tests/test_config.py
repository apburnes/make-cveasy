"""Tests for configuration management."""

import pytest
import os
from unittest.mock import patch

from cveasy.config import get_ai_provider


def test_get_ai_provider_with_value():
    """Test get_ai_provider returns configured provider."""
    with patch.dict(os.environ, {"CVEASY_AI_PROVIDER": "anthropic"}):
        provider = get_ai_provider()
        assert provider == "anthropic"


def test_get_ai_provider_case_insensitive():
    """Test get_ai_provider normalizes to lowercase."""
    with patch.dict(os.environ, {"CVEASY_AI_PROVIDER": "ANTHROPIC"}):
        provider = get_ai_provider()
        assert provider == "anthropic"


def test_get_ai_provider_strips_whitespace():
    """Test get_ai_provider strips whitespace."""
    with patch.dict(os.environ, {"CVEASY_AI_PROVIDER": "  openai  "}):
        provider = get_ai_provider()
        assert provider == "openai"


def test_get_ai_provider_missing_raises_error():
    """Test get_ai_provider raises error when not configured."""
    with patch.dict(os.environ, {}, clear=True):
        # Remove CVEASY_AI_PROVIDER if it exists
        os.environ.pop("CVEASY_AI_PROVIDER", None)

        with pytest.raises(ValueError) as exc_info:
            get_ai_provider()

        error_msg = str(exc_info.value)
        assert "CVEASY_AI_PROVIDER environment variable is not set" in error_msg
        assert ".env file" in error_msg
        assert "CVEASY_AI_PROVIDER=openai" in error_msg or "CVEASY_AI_PROVIDER" in error_msg


def test_get_ai_provider_empty_string_raises_error():
    """Test get_ai_provider raises error when set to empty string."""
    with patch.dict(os.environ, {"CVEASY_AI_PROVIDER": ""}):
        with pytest.raises(ValueError) as exc_info:
            get_ai_provider()

        error_msg = str(exc_info.value)
        assert "CVEASY_AI_PROVIDER is set but empty" in error_msg
        assert "openai, anthropic, or openrouter" in error_msg


def test_get_ai_provider_whitespace_only_raises_error():
    """Test get_ai_provider raises error when set to whitespace only."""
    with patch.dict(os.environ, {"CVEASY_AI_PROVIDER": "   "}):
        with pytest.raises(ValueError) as exc_info:
            get_ai_provider()

        error_msg = str(exc_info.value)
        assert "CVEASY_AI_PROVIDER is set but empty" in error_msg


def test_get_ai_provider_error_message_includes_env_instructions():
    """Test that error message includes helpful instructions about .env file."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CVEASY_AI_PROVIDER", None)

        with pytest.raises(ValueError) as exc_info:
            get_ai_provider()

        error_msg = str(exc_info.value)
        # Check that error message mentions .env file configuration
        assert ".env" in error_msg.lower()
        # Check that it mentions the environment variable name
        assert "CVEASY_AI_PROVIDER" in error_msg
        # Check that it mentions copying .env.example
        assert ".env.example" in error_msg.lower()
        # Check that it mentions the provider options
        assert "openai" in error_msg.lower() or "anthropic" in error_msg.lower() or "openrouter" in error_msg.lower()
