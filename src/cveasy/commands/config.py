"""Config command for setting environment variables."""

from pathlib import Path
from typing import Optional
import typer
import click

from cveasy.config import get_project_path
from cveasy.cli_utils import handle_errors


def _get_default_model(provider: str) -> str:
    """Get default model for a provider."""
    defaults = {
        "openai": "gpt-4",
        "anthropic": "claude-haiku-4-5",
        "openrouter": "openai/gpt-4",
    }
    return defaults.get(provider.lower(), "gpt-4")


def _read_env_file(env_file: Path) -> dict:
    """Read existing .env file and return variables as dict."""
    if not env_file.exists():
        return {}

    env_vars = {}
    try:
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip comments and empty lines
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=VALUE format
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    env_vars[key] = value
    except Exception:
        pass  # If we can't read it, return empty dict

    return env_vars


def _write_env_file(env_file: Path, variables: dict, preserve_other: bool = True):
    """Write variables to .env file, preserving existing content if preserve_other is True."""
    existing_vars = _read_env_file(env_file) if preserve_other else {}

    # Merge with new variables (new ones take precedence)
    existing_vars.update(variables)

    # Read existing file to preserve comments and structure
    existing_lines = []
    if env_file.exists() and preserve_other:
        try:
            with open(env_file, "r", encoding="utf-8") as f:
                existing_lines = f.readlines()
        except Exception:
            existing_lines = []

    # Track which variables we've written
    written_vars = set()

    # Write file
    with open(env_file, "w", encoding="utf-8") as f:
        # First, update existing lines
        for line in existing_lines:
            stripped = line.strip()
            # Skip empty lines and comments (we'll add them back)
            if not stripped or stripped.startswith("#"):
                # Check if this is a comment about one of our variables
                if any(var in stripped for var in variables.keys()):
                    continue  # Skip old comments for variables we're updating
                f.write(line)
                continue

            # Check if this line defines one of our variables
            if "=" in stripped:
                key = stripped.split("=", 1)[0].strip()
                if key in variables:
                    # Write updated value
                    f.write(f"{key}={existing_vars[key]}\n")
                    written_vars.add(key)
                    continue
                else:
                    # Write line as-is if it's not one of our variables
                    f.write(line)
                    continue

            # Write non-variable lines (empty lines, etc.) as-is
            f.write(line)

        # Add any variables that weren't in the file
        for key, value in variables.items():
            if key not in written_vars:
                f.write(f"{key}={value}\n")


@handle_errors
def config(
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Project directory path (optional)",
    ),
):
    """
    Configure CVEasy environment variables interactively.

    This command prompts you through setting up:
    - CVEASY_AI_PROVIDER: AI provider to use (openai, anthropic, or openrouter)
    - CVEASY_API_KEY: Your API key for the selected provider
    - CVEASY_MODEL: Model name to use (optional, with provider-specific defaults)
    - CVEASY_MAX_TOKENS: Maximum tokens for responses (default: 8192)
    - CVEASY_SPACY_MODEL: spaCy language model to use (default: en_core_web_sm)

    The configuration is saved to the .env file in your project root.

    Examples:
        cveasy config
        cveasy config --project /path/to/project
    """
    project_path = get_project_path(project)
    env_file = project_path / ".env"

    # Read existing values
    existing_vars = _read_env_file(env_file)

    typer.echo("Configure CVEasy environment variables")
    typer.echo("=" * 50)

    # Prompt for AI Provider with choice selection
    current_provider = existing_vars.get("CVEASY_AI_PROVIDER", "")
    valid_providers = ["openai", "anthropic", "openrouter"]
    default_provider = current_provider if current_provider in valid_providers else "openai"

    provider = typer.prompt(
        "AI Provider",
        default=default_provider,
        type=click.Choice(valid_providers, case_sensitive=False),
    )
    provider = provider.lower().strip()

    # Prompt for API Key
    current_api_key = existing_vars.get("CVEASY_API_KEY", "")
    api_key = typer.prompt(
        "API Key",
        default=current_api_key if current_api_key else None,
        hide_input=True,
    )
    if not api_key:
        typer.echo("Error: API Key is required", err=True)
        raise typer.Exit(1)

    # Prompt for Model
    current_model = existing_vars.get("CVEASY_MODEL", "")
    default_model = current_model if current_model else _get_default_model(provider)
    model = typer.prompt(
        "Model",
        default=default_model,
    )

    # Prompt for Max Tokens
    current_max_tokens = existing_vars.get("CVEASY_MAX_TOKENS", "8192")
    max_tokens = typer.prompt(
        "Max Tokens",
        default=current_max_tokens,
        type=int,
    )

    # Prompt for spaCy Model
    current_spacy_model = existing_vars.get("CVEASY_SPACY_MODEL", "en_core_web_sm")
    spacy_model = typer.prompt(
        "spaCy Model",
        default=current_spacy_model,
    )

    # Write to .env file
    variables = {
        "CVEASY_AI_PROVIDER": provider,
        "CVEASY_API_KEY": api_key,
        "CVEASY_MODEL": model,
        "CVEASY_MAX_TOKENS": str(max_tokens),
        "CVEASY_SPACY_MODEL": spacy_model,
    }

    _write_env_file(env_file, variables, preserve_other=True)

    typer.echo(f"\n✅ Configuration saved to {env_file}")
    typer.echo(f"\nConfigured values:")
    typer.echo(f"  AI Provider: {provider}")
    typer.echo(f"  Model: {model}")
    typer.echo(f"  Max Tokens: {max_tokens}")
    typer.echo(f"  spaCy Model: {spacy_model}")
