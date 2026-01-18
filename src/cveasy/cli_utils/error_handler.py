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
    ImportError,
    ExportError,
    ProjectError,
)


def handle_errors(func):
    """
    Decorator to handle CVEasy exceptions consistently.

    This decorator catches CVEasy exceptions and converts them to
    user-friendly error messages with appropriate exit codes.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NotFoundError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)
        except ValidationError as e:
            typer.echo(f"Validation Error: {e}", err=True)
            raise typer.Exit(1)
        except StorageError as e:
            typer.echo(f"Storage Error: {e}", err=True)
            raise typer.Exit(1)
        except AIProviderError as e:
            typer.echo(f"AI Provider Error: {e}", err=True)
            raise typer.Exit(1)
        except ResumeGenerationError as e:
            typer.echo(f"Resume Generation Error: {e}", err=True)
            raise typer.Exit(1)
        except ImportError as e:
            typer.echo(f"Import Error: {e}", err=True)
            raise typer.Exit(1)
        except ExportError as e:
            typer.echo(f"Export Error: {e}", err=True)
            raise typer.Exit(1)
        except ProjectError as e:
            typer.echo(f"Project Error: {e}", err=True)
            raise typer.Exit(1)
        except CVEasyError as e:
            typer.echo(f"Error: {e}", err=True)
            raise typer.Exit(1)

    return wrapper
