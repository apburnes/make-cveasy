"""Version command to display CVEasy version."""

import typer

from cveasy import __version__
from cveasy.cli_utils import handle_errors

# Create app for backward compatibility if needed
app = typer.Typer()


@app.command()
@handle_errors
def version():
    """
    Display the current version of CVEasy.

    Examples:
        cveasy version
    """
    typer.echo(__version__)
