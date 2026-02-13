"""Configuration management for CVEasy."""

import os
import threading
from pathlib import Path
from typing import Optional

_config_lock = threading.RLock()

# Track if we've loaded the .env file from project root
_env_loaded_from_project = False

# Cache for project root to avoid repeated filesystem traversal
_project_root_cache: Optional[Path] = None
_project_root_cache_path: Optional[Path] = None


def _load_env_from_project_root():
    """Load .env file from project root if it exists. Thread-safe."""
    global _env_loaded_from_project
    if _env_loaded_from_project:
        return

    with _config_lock:
        # Double-check after acquiring lock
        if _env_loaded_from_project:
            return

        try:
            from dotenv import load_dotenv
        except ImportError:
            return  # python-dotenv not installed, skip

        # Try to find project root and load .env from there
        project_root = find_project_root()
        if project_root:
            env_file = project_root / ".env"
            if env_file.exists():
                load_dotenv(env_file, override=True)
                _env_loaded_from_project = True
                return

        # If no project root found, search up the directory tree for .env
        current = Path.cwd().resolve()
        for path in [current] + list(current.parents):
            env_file = path / ".env"
            if env_file.exists():
                load_dotenv(env_file, override=True)
                _env_loaded_from_project = True
                return

        # Fallback: try current directory (default behavior)
        load_dotenv()
        _env_loaded_from_project = True


# Removed eager loading - now only loads when _load_env_from_project_root() is called


def find_project_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the project root directory by looking for .git directory or resume subdirectories.

    Uses caching to avoid repeated filesystem traversal. Thread-safe.

    Args:
        start_path: Starting path for search. Defaults to current working directory.

    Returns:
        Path to project root if found, None otherwise.
    """
    global _project_root_cache, _project_root_cache_path

    if start_path is None:
        start_path = Path.cwd()

    start_path = Path(start_path).resolve()

    with _config_lock:
        # Check cache first
        if _project_root_cache is not None and _project_root_cache_path == start_path:
            return _project_root_cache

        current = start_path
        expected_subdirs = [
            "skills", "experiences", "stories", "links", "projects", "applications",
        ]

        # Check if we're in a project directory
        for path in [current] + list(current.parents):
            # Check for .git directory
            if (path / ".git").exists():
                # Verify it has the expected structure
                if all((path / subdir).exists() for subdir in expected_subdirs):
                    _project_root_cache = path
                    _project_root_cache_path = start_path
                    return path

            # Also check for expected subdirectories without .git
            if all((path / subdir).exists() for subdir in expected_subdirs):
                _project_root_cache = path
                _project_root_cache_path = start_path
                return path

        # Cache None result too
        _project_root_cache = None
        _project_root_cache_path = start_path
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
    """
    Get the configured AI provider from environment variables.

    Returns:
        The AI provider name (openai, anthropic, or openrouter)

    Raises:
        ValueError: If CVEASY_AI_PROVIDER is not set in environment variables or .env file
    """
    # Ensure .env file is loaded from project root
    _load_env_from_project_root()
    provider = os.getenv("CVEASY_AI_PROVIDER")

    # Check if the environment variable is not set at all
    if provider is None:
        raise ValueError(
            "CVEASY_AI_PROVIDER environment variable is not set. "
            "Please configure your .env file with:\n"
            "  CVEASY_AI_PROVIDER=openai  # or 'anthropic' or 'openrouter'\n"
            "  CVEASY_API_KEY=your_key_here\n"
            "\n"
            "You can use 'cveasy config' to configure interactively, or copy .env.example to .env and update it."
        )

    # Normalize to lowercase for case-insensitive matching
    provider = provider.lower().strip()

    # Check if the environment variable is set but empty (after stripping whitespace)
    if not provider:
        raise ValueError(
            "CVEASY_AI_PROVIDER is set but empty. "
            "Please set it to one of: openai, anthropic, or openrouter"
        )

    return provider


def get_openai_api_key() -> Optional[str]:
    """Get OpenAI API key from environment variables."""
    _load_env_from_project_root()
    return os.getenv("OPENAI_API_KEY")


def get_anthropic_api_key() -> Optional[str]:
    """Get Anthropic API key from environment variables."""
    _load_env_from_project_root()
    return os.getenv("ANTHROPIC_API_KEY")


def get_openrouter_api_key() -> Optional[str]:
    """Get OpenRouter API key from environment variables."""
    _load_env_from_project_root()
    return os.getenv("OPENROUTER_API_KEY")


def get_cveasy_api_key() -> Optional[str]:
    """Get unified API key from environment variables."""
    _load_env_from_project_root()
    return os.getenv("CVEASY_API_KEY")


def get_cveasy_model() -> Optional[str]:
    """Get unified model name from environment variables."""
    _load_env_from_project_root()
    return os.getenv("CVEASY_MODEL")


def get_cveasy_max_tokens() -> int:
    """Get unified max tokens from environment variables."""
    _load_env_from_project_root()
    max_tokens = os.getenv("CVEASY_MAX_TOKENS", "8192")
    try:
        return int(max_tokens)
    except ValueError:
        return 8192  # Default if invalid value


def get_spacy_model() -> str:
    """Get spaCy model name. Always returns en_core_web_sm (hard-coded)."""
    return "en_core_web_sm"
