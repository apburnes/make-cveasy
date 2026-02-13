"""Error handling middleware for CLI commands."""

from functools import wraps
import typer

from cveasy.exceptions import (
    CVEasyError,
    NotFoundError,
    ValidationError,
    StorageError,
    AIProviderError,
    ResumeGenerationError,
    DataImportError,
    ExportError,
    ProjectError,
)

_ERROR_LABELS = {
    NotFoundError: "Error",
    ValidationError: "Validation Error",
    StorageError: "Storage Error",
    AIProviderError: "AI Provider Error",
    ResumeGenerationError: "Resume Generation Error",
    DataImportError: "Import Error",
    ExportError: "Export Error",
    ProjectError: "Project Error",
    CVEasyError: "Error",
}

_RECOVERY_HINTS = {
    AIProviderError: (
        "Check your API key (CVEASY_API_KEY), provider (CVEASY_AI_PROVIDER), "
        "and model (CVEASY_MODEL) in your .env file. Run 'cveasy config' to reconfigure."
    ),
    StorageError: "Check file permissions and available disk space in your project directory.",
    DataImportError: (
        "Verify the file exists, is not corrupted, and is in a supported format (PDF or DOCX)."
    ),
    ResumeGenerationError: (
        "This may be a transient API issue. Try again, or check your AI provider "
        "configuration with 'cveasy config'."
    ),
    ExportError: "Ensure the output directory exists and you have write permissions.",
    ProjectError: (
        "Run 'cveasy init' to create a new project, or use --project to specify the path."
    ),
    ValidationError: "Check your input values. Run the command with --help for usage details.",
}


def _handle_cveasy_error(error: CVEasyError) -> None:
    """Display error message with optional recovery hint, then exit."""
    label = _ERROR_LABELS.get(type(error), "Error")
    typer.echo(f"{label}: {error}", err=True)

    hint = _RECOVERY_HINTS.get(type(error))
    if hint:
        typer.echo(f"  Hint: {hint}", err=True)

    raise typer.Exit(1)


def handle_errors(func):
    """
    Decorator to handle CVEasy exceptions consistently.

    This decorator catches CVEasy exceptions and converts them to
    user-friendly error messages with appropriate exit codes and recovery hints.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except CVEasyError as e:
            _handle_cveasy_error(e)

    return wrapper
