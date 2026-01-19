"""Check command for resume quality analysis."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import CheckService
from cveasy.cli_utils import handle_errors
from cveasy.ai.metered_provider import MeteredAIProvider

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

    # Reset token counter before starting
    MeteredAIProvider.reset_total_tokens()

    typer.echo(f"Checking resume against job description...")
    report, filepath = service.check_resume(application_id)

    # Get token usage
    total_tokens = MeteredAIProvider.get_total_tokens()
    input_tokens = MeteredAIProvider.get_input_tokens()
    output_tokens = MeteredAIProvider.get_output_tokens()

    typer.echo(f"✅ Check report saved to: {filepath}")
    typer.echo(f"\n💡 Tip: Review the report and run 'cveasy generate --application {application_id} --update' to improve your resume")

    # Display token usage
    if total_tokens > 0:
        typer.echo(f"\n📊 Token Usage:")
        typer.echo(f"   Input tokens: {input_tokens:,}")
        typer.echo(f"   Output tokens: {output_tokens:,}")
        typer.echo(f"   Total tokens: {total_tokens:,}")
