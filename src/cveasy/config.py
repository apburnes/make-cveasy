"""Configuration management for CVEasy."""

import os
from pathlib import Path
from typing import Optional

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, skip


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the project root directory by looking for .git directory or resume subdirectories.

    Args:
        start_path: Starting path for search. Defaults to current working directory.

    Returns:
        Path to project root if found, None otherwise.
    """
    if start_path is None:
        start_path = Path.cwd()

    current = Path(start_path).resolve()

    # Check if we're in a project directory
    for path in [current] + list(current.parents):
        # Check for .git directory
        if (path / ".git").exists():
            # Verify it has the expected structure
            if all((path / subdir).exists() for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]):
                return path

        # Also check for expected subdirectories without .git
        if all((path / subdir).exists() for subdir in ["skills", "experiences", "stories", "links", "projects", "applications"]):
            return path

    return None


def get_project_path(project_path: Optional[str] = None) -> Path:
    """
    Get the project path, either from argument or by finding it.

    Args:
        project_path: Explicit project path from --project flag.

    Returns:
        Path to project root.

    Raises:
        ValueError: If project path cannot be determined.
    """
    if project_path:
        path = Path(project_path).resolve()
        if not path.exists():
            raise ValueError(f"Project path does not exist: {project_path}")
        return path

    found = find_project_root()
    if found is None:
        raise ValueError(
            "Not in a CVEasy project directory. Run 'cveasy init' first or use --project flag."
        )
    return found


def get_ai_provider() -> str:
    """Get the configured AI provider from environment variables."""
    return os.getenv("CVEASY_AI_PROVIDER", "openai")


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment variables."""
    return os.getenv("OPENAI_API_KEY")


def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment variables."""
    return os.getenv("ANTHROPIC_API_KEY")


def get_openrouter_api_key() -> Optional[str]:
    """Get OpenRouter API key from environment variables."""
    return os.getenv("OPENROUTER_API_KEY")
