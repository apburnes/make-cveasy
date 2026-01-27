"""Tests for configuration management."""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from cveasy.config import (
    get_ai_provider,
    find_project_root,
    get_project_path,
    get_openai_api_key,
    get_anthropic_api_key,
    get_openrouter_api_key,
    get_cveasy_api_key,
    get_cveasy_model,
    get_cveasy_max_tokens,
    get_spacy_model,
)


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


def test_find_project_root_with_git_and_subdirs():
    """Test find_project_root finds project with .git and subdirectories."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create .git directory
        (project_path / ".git").mkdir()

        # Create required subdirectories
        for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
            (project_path / subdir).mkdir()

        found = find_project_root(project_path)
        assert found is not None
        assert found.resolve() == project_path.resolve()


def test_find_project_root_with_subdirs_only():
    """Test find_project_root finds project with subdirectories but no .git."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create required subdirectories (no .git)
        for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
            (project_path / subdir).mkdir()

        found = find_project_root(project_path)
        assert found is not None
        assert found.resolve() == project_path.resolve()


def test_find_project_root_in_subdirectory():
    """Test find_project_root finds project when called from subdirectory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        subdir = project_path / "some" / "nested" / "directory"
        subdir.mkdir(parents=True)

        # Create .git and subdirectories at project root
        (project_path / ".git").mkdir()
        for subdir_name in ["skills", "experiences", "stories", "links", "projects", "applications"]:
            (project_path / subdir_name).mkdir()

        found = find_project_root(subdir)
        assert found is not None
        assert found.resolve() == project_path.resolve()


def test_find_project_root_not_found():
    """Test find_project_root returns None when no project found."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        # Don't create any project structure

        found = find_project_root(project_path)
        assert found is None


def test_find_project_root_with_start_path():
    """Test find_project_root with explicit start_path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create required subdirectories
        for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
            (project_path / subdir).mkdir()

        found = find_project_root(project_path)
        assert found is not None
        assert found.resolve() == project_path.resolve()


def test_get_project_path_with_explicit_path():
    """Test get_project_path with explicit path argument."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        result = get_project_path(str(project_path))
        assert result == project_path.resolve()


def test_get_project_path_with_explicit_nonexistent_path():
    """Test get_project_path raises error for nonexistent path."""
    with pytest.raises(ValueError) as exc_info:
        get_project_path("/nonexistent/path/that/does/not/exist")

    assert "does not exist" in str(exc_info.value)


def test_get_project_path_finds_project():
    """Test get_project_path finds project when no explicit path given."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create required subdirectories
        for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
            (project_path / subdir).mkdir()

        with patch("cveasy.config.find_project_root", return_value=project_path):
            result = get_project_path(None)
            assert result == project_path


def test_get_project_path_not_found():
    """Test get_project_path raises error when project not found."""
    with patch("cveasy.config.find_project_root", return_value=None):
        with pytest.raises(ValueError) as exc_info:
            get_project_path(None)

        assert "Not in a CVEasy project directory" in str(exc_info.value)
        assert "--project flag" in str(exc_info.value)


def test_get_openai_api_key():
    """Test get_openai_api_key returns API key from environment."""
    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
        # Reset the module-level flag to allow reloading
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_openai_api_key()
        assert key == "test-key-123"


def test_get_openai_api_key_not_set():
    """Test get_openai_api_key returns None when not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("OPENAI_API_KEY", None)

        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_openai_api_key()
        assert key is None


def test_get_anthropic_api_key():
    """Test get_anthropic_api_key returns API key from environment."""
    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key-456"}):
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_anthropic_api_key()
        assert key == "test-key-456"


def test_get_anthropic_api_key_not_set():
    """Test get_anthropic_api_key returns None when not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("ANTHROPIC_API_KEY", None)

        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_anthropic_api_key()
        assert key is None


def test_get_openrouter_api_key():
    """Test get_openrouter_api_key returns API key from environment."""
    with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-key-789"}):
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_openrouter_api_key()
        assert key == "test-key-789"


def test_get_openrouter_api_key_not_set():
    """Test get_openrouter_api_key returns None when not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("OPENROUTER_API_KEY", None)

        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_openrouter_api_key()
        assert key is None


def test_get_cveasy_api_key():
    """Test get_cveasy_api_key returns API key from environment."""
    with patch.dict(os.environ, {"CVEASY_API_KEY": "test-key-unified"}):
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_cveasy_api_key()
        assert key == "test-key-unified"


def test_get_cveasy_api_key_not_set():
    """Test get_cveasy_api_key returns None when not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CVEASY_API_KEY", None)

        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        key = get_cveasy_api_key()
        assert key is None


def test_get_cveasy_model():
    """Test get_cveasy_model returns model from environment."""
    with patch.dict(os.environ, {"CVEASY_MODEL": "gpt-4-turbo"}):
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        model = get_cveasy_model()
        assert model == "gpt-4-turbo"


def test_get_cveasy_model_not_set():
    """Test get_cveasy_model returns None when not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CVEASY_MODEL", None)

        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        model = get_cveasy_model()
        assert model is None


def test_get_cveasy_max_tokens():
    """Test get_cveasy_max_tokens returns max tokens from environment."""
    with patch.dict(os.environ, {"CVEASY_MAX_TOKENS": "4096"}):
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        max_tokens = get_cveasy_max_tokens()
        assert max_tokens == 4096


def test_get_cveasy_max_tokens_default():
    """Test get_cveasy_max_tokens returns default when not set."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CVEASY_MAX_TOKENS", None)

        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        max_tokens = get_cveasy_max_tokens()
        assert max_tokens == 8192  # Default value


def test_get_cveasy_max_tokens_invalid_defaults():
    """Test get_cveasy_max_tokens returns default when invalid value."""
    with patch.dict(os.environ, {"CVEASY_MAX_TOKENS": "invalid"}):
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        max_tokens = get_cveasy_max_tokens()
        assert max_tokens == 8192  # Should default on invalid value


def test_get_spacy_model():
    """Test get_spacy_model always returns en_core_web_sm (hard-coded)."""
    # Model is now hard-coded, so it should always return en_core_web_sm
    # regardless of environment variables
    with patch.dict(os.environ, {"CVEASY_SPACY_MODEL": "en_core_web_md"}):
        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        model = get_spacy_model()
        assert model == "en_core_web_sm"  # Always returns hard-coded value


def test_get_spacy_model_default():
    """Test get_spacy_model always returns en_core_web_sm (hard-coded)."""
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("CVEASY_SPACY_MODEL", None)

        import cveasy.config
        cveasy.config._env_loaded_from_project = False

        model = get_spacy_model()
        assert model == "en_core_web_sm"  # Always returns hard-coded value
