"""Check command for resume quality analysis."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import CheckService
from cveasy.cli_utils import handle_errors

app = typer.Typer(
    help="Check resume quality against job descriptions",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
@handle_errors
def check(
    application_id: str = typer.Option(..., "-a", "--application", help="Application ID to run resume check for"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Check resume quality against job description.

    Automatically generates resume if it doesn't exist, then performs quality check
    and saves check-report.md to the application directory.

    Usage:
        cveasy check --application <application-id>
        cveasy check -a <application-id> --project /path/to/project
    """
    project_path = get_project_path(project)
    service = CheckService(project_path)

    typer.echo(f"Checking resume against job description...")
    report, filepath = service.check_resume(application_id)

    typer.echo(f"✅ Check report saved to: {filepath}")
    typer.echo(f"\n💡 Tip: Review the report and run 'cveasy generate --application {application_id} --update' to improve your resume")
