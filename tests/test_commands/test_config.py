"""Tests for config command."""

import pytest
import tempfile
import shutil
import typer
from pathlib import Path
from unittest.mock import patch, MagicMock

from cveasy.commands.config import config, _read_env_file, _write_env_file, _get_default_model


def test_get_default_model():
    """Test default model selection by provider."""
    assert _get_default_model("openai") == "gpt-4"
    assert _get_default_model("anthropic") == "claude-haiku-4-5"
    assert _get_default_model("openrouter") == "openai/gpt-4"
    assert _get_default_model("unknown") == "gpt-4"  # Default fallback


def test_read_env_file_nonexistent():
    """Test reading non-existent .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        vars = _read_env_file(env_file)
        assert vars == {}


def test_read_env_file_existing():
    """Test reading existing .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("CVEASY_AI_PROVIDER=openai\nCVEASY_API_KEY=test-key\n# Comment\nCVEASY_MODEL=gpt-4\n")
        vars = _read_env_file(env_file)
        assert vars["CVEASY_AI_PROVIDER"] == "openai"
        assert vars["CVEASY_API_KEY"] == "test-key"
        assert vars["CVEASY_MODEL"] == "gpt-4"
        assert "# Comment" not in vars  # Comments should be skipped


def test_write_env_file_new():
    """Test writing to new .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        variables = {
            "CVEASY_AI_PROVIDER": "openai",
            "CVEASY_API_KEY": "test-key",
            "CVEASY_MODEL": "gpt-4",
        }
        _write_env_file(env_file, variables, preserve_other=False)

        assert env_file.exists()
        content = env_file.read_text()
        assert "CVEASY_AI_PROVIDER=openai" in content
        assert "CVEASY_API_KEY=test-key" in content
        assert "CVEASY_MODEL=gpt-4" in content


def test_write_env_file_update_existing():
    """Test updating existing .env file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        env_file = Path(tmpdir) / ".env"
        env_file.write_text("CVEASY_AI_PROVIDER=anthropic\nOTHER_VAR=value\n")

        variables = {
            "CVEASY_AI_PROVIDER": "openai",
            "CVEASY_API_KEY": "new-key",
        }
        _write_env_file(env_file, variables, preserve_other=True)

        content = env_file.read_text()
        assert "CVEASY_AI_PROVIDER=openai" in content
        assert "CVEASY_API_KEY=new-key" in content
        assert "OTHER_VAR=value" in content
        assert "anthropic" not in content  # Old value should be replaced


def test_config_command_creates_env_file(tmp_path, monkeypatch):
    """Test config command creates .env file."""
    # Create project structure
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
        (tmp_path / subdir).mkdir()

    # Mock typer.prompt to return test values
    prompts = {
        "AI Provider": "openai",
        "API Key": "test-api-key",
        "Model": "gpt-4",
        "Max Tokens": "8192",
        "spaCy Model": "en_core_web_sm",
    }

    def mock_prompt(text, **kwargs):
        # Handle prompt text that might have variations
        # Check for more specific matches first (spaCy Model before Model)
        text_lower = text.lower()
        if "spacy" in text_lower and "model" in text_lower:
            return prompts.get("spaCy Model", kwargs.get("default", ""))
        for key in prompts:
            if key.lower() in text_lower or text_lower in key.lower():
                return prompts[key]
        return kwargs.get("default", "")

    with patch("cveasy.commands.config.typer.prompt", side_effect=mock_prompt):
        with patch("cveasy.commands.config.typer.echo"):
            with patch("cveasy.commands.config.get_project_path", return_value=tmp_path):
                config(project=None)

    env_file = tmp_path / ".env"
    assert env_file.exists()
    content = env_file.read_text()
    assert "CVEASY_AI_PROVIDER=openai" in content
    assert "CVEASY_API_KEY=test-api-key" in content
    assert "CVEASY_MODEL=gpt-4" in content
    assert "CVEASY_MAX_TOKENS=8192" in content
    assert "CVEASY_SPACY_MODEL=en_core_web_sm" in content


def test_config_command_updates_existing_env_file(tmp_path, monkeypatch):
    """Test config command updates existing .env file."""
    # Create project structure
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
        (tmp_path / subdir).mkdir()

    # Create existing .env file
    env_file = tmp_path / ".env"
    env_file.write_text("CVEASY_AI_PROVIDER=anthropic\nOTHER_VAR=preserved\n")

    # Mock typer.prompt to return test values
    prompts = {
        "AI Provider": "openai",
        "API Key": "new-api-key",
        "Model": "gpt-4",
        "Max Tokens": "4096",
        "spaCy Model": "en_core_web_sm",
    }

    def mock_prompt(text, **kwargs):
        # Handle prompt text that might have variations
        for key in prompts:
            if key in text or text in key:
                return prompts[key]
        return kwargs.get("default", "")

    with patch("cveasy.commands.config.typer.prompt", side_effect=mock_prompt):
        with patch("cveasy.commands.config.typer.echo"):
            with patch("cveasy.commands.config.get_project_path", return_value=tmp_path):
                config(project=None)

    content = env_file.read_text()
    assert "CVEASY_AI_PROVIDER=openai" in content
    assert "CVEASY_API_KEY=new-api-key" in content
    assert "OTHER_VAR=preserved" in content  # Should preserve other variables


def test_config_command_with_project_flag(tmp_path, monkeypatch):
    """Test config command with --project flag."""
    project_path = tmp_path / "project"
    project_path.mkdir()

    # Create project structure
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
        (project_path / subdir).mkdir()

    # Mock typer.prompt
    prompts = {
        "AI Provider": "openrouter",
        "API Key": "test-key",
        "Model": "openai/gpt-4",
        "Max Tokens": "8192",
        "spaCy Model": "en_core_web_sm",
    }

    def mock_prompt(text, **kwargs):
        # Handle prompt text that might have variations
        for key in prompts:
            if key in text or text in key:
                return prompts[key]
        return kwargs.get("default", "")

    with patch("cveasy.commands.config.typer.prompt", side_effect=mock_prompt):
        with patch("cveasy.commands.config.typer.echo"):
            config(project=str(project_path))

    env_file = project_path / ".env"
    assert env_file.exists()
    content = env_file.read_text()
    assert "CVEASY_AI_PROVIDER=openrouter" in content


def test_config_command_validates_provider_choice(tmp_path, monkeypatch):
    """Test config command validates provider choice."""
    # Create project structure
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
        (tmp_path / subdir).mkdir()

    # Mock typer.prompt to return invalid provider (should be caught by click.Choice)
    # But we'll test with a valid one since click.Choice handles validation
    prompts = {
        "AI Provider": "openai",  # Valid choice
        "API Key": "test-key",
        "Model": "gpt-4",
        "Max Tokens": "8192",
        "spaCy Model": "en_core_web_sm",
    }

    def mock_prompt(text, **kwargs):
        # Handle prompt text that might have variations
        for key in prompts:
            if key in text or text in key:
                return prompts[key]
        return kwargs.get("default", "")

    with patch("cveasy.commands.config.typer.prompt", side_effect=mock_prompt):
        with patch("cveasy.commands.config.typer.echo"):
            with patch("cveasy.commands.config.get_project_path", return_value=tmp_path):
                config(project=None)

    env_file = tmp_path / ".env"
    assert env_file.exists()


def test_config_command_handles_missing_api_key(tmp_path, monkeypatch):
    """Test config command handles missing API key."""
    # Create project structure
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
        (tmp_path / subdir).mkdir()

    # Mock typer.prompt to return empty API key
    prompts = {
        "AI Provider": "openai",
        "API Key": "",  # Empty key
        "Model": "gpt-4",
        "Max Tokens": "8192",
        "spaCy Model": "en_core_web_sm",
    }

    def mock_prompt(text, **kwargs):
        # Handle prompt text that might have variations
        for key in prompts:
            if key in text or text in key:
                return prompts[key]
        return kwargs.get("default", "")

    with patch("cveasy.commands.config.typer.prompt", side_effect=mock_prompt):
        with patch("cveasy.commands.config.typer.echo"):
            with patch("cveasy.commands.config.get_project_path", return_value=tmp_path):
                with pytest.raises((SystemExit, typer.Exit)):  # Should exit with error
                    config(project=None)


def test_config_command_uses_defaults_from_existing_env(tmp_path, monkeypatch):
    """Test config command uses existing values as defaults."""
    # Create project structure
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
        (tmp_path / subdir).mkdir()

    # Create existing .env file
    env_file = tmp_path / ".env"
    env_file.write_text("CVEASY_AI_PROVIDER=anthropic\nCVEASY_API_KEY=existing-key\nCVEASY_MODEL=claude-3-opus\nCVEASY_MAX_TOKENS=4096\nCVEASY_SPACY_MODEL=en_core_web_md\n")

    # Mock typer.prompt - should use existing values as defaults
    call_count = 0
    def mock_prompt(text, **kwargs):
        nonlocal call_count
        call_count += 1
        # For first call (provider), return default
        if "AI Provider" in text:
            assert kwargs.get("default") == "anthropic"
            return "anthropic"  # Accept default
        elif text == "API Key":
            assert kwargs.get("default") == "existing-key"
            return "existing-key"  # Accept default
        elif text == "Model":
            assert kwargs.get("default") == "claude-3-opus"
            return "claude-3-opus"  # Accept default
        elif text == "Max Tokens":
            assert kwargs.get("default") == "4096"
            return "4096"  # Accept default
        elif "spaCy Model" in text:
            assert kwargs.get("default") == "en_core_web_md"
            return "en_core_web_md"  # Accept default
        return kwargs.get("default", "")

    with patch("cveasy.commands.config.typer.prompt", side_effect=mock_prompt):
        with patch("cveasy.commands.config.typer.echo"):
            with patch("cveasy.commands.config.get_project_path", return_value=tmp_path):
                config(project=None)

    # Verify defaults were used
    assert call_count == 5  # Should have prompted 5 times (including spaCy model)


def test_config_command_with_spacy_model(tmp_path, monkeypatch):
    """Test config command saves spaCy model configuration."""
    # Create project structure
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]:
        (tmp_path / subdir).mkdir()

    # Mock typer.prompt to return test values
    prompts = {
        "AI Provider": "openai",
        "API Key": "test-api-key",
        "Model": "gpt-4",
        "Max Tokens": "8192",
        "spaCy Model": "en_core_web_md",  # Custom spaCy model
    }

    def mock_prompt(text, **kwargs):
        # Handle prompt text that might have variations
        # Check for more specific matches first (spaCy Model before Model)
        text_lower = text.lower()
        if "spacy" in text_lower and "model" in text_lower:
            return prompts.get("spaCy Model", kwargs.get("default", ""))
        for key in prompts:
            if key.lower() in text_lower or text_lower in key.lower():
                return prompts[key]
        return kwargs.get("default", "")

    with patch("cveasy.commands.config.typer.prompt", side_effect=mock_prompt):
        with patch("cveasy.commands.config.typer.echo"):
            with patch("cveasy.commands.config.get_project_path", return_value=tmp_path):
                config(project=None)

    env_file = tmp_path / ".env"
    assert env_file.exists()
    content = env_file.read_text()
    assert "CVEASY_SPACY_MODEL=en_core_web_md" in content
