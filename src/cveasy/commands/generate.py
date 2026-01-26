"""Generate command for creating resumes."""

from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import ResumeService
from cveasy.cli_utils import handle_errors
from cveasy.ai.metered_provider import MeteredAIProvider

app = typer.Typer(
    help="Generate resumes using AI",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
@handle_errors
def generate(
    application: Optional[str] = typer.Option(
        None, "--application", "-a", help="Application ID to generate customized resume for"
    ),
    update: bool = typer.Option(
        False, "--update", "-u", help="Update resume based on check report (requires --application)"
    ),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project directory path"),
):
    """
    Generate a resume.

    If --application is specified, generates a customized resume for that job application.
    Otherwise, generates a general resume from all available data.

    Use --update flag with --application to improve resume based on check report.

    Examples:
        cveasy generate
        cveasy generate --application software-engineer-20240115
        cveasy generate --application software-engineer-20240115 --update
    """
    project_path = get_project_path(project)
    service = ResumeService(project_path)

    # Reset token counter before starting
    MeteredAIProvider.reset_total_tokens()

    if application:
        if update:
            typer.echo(f"Updating resume for application '{application}' based on check report...")
            filepath = service.update_resume_from_check_report(application)
        else:
            typer.echo(f"Generating customized resume for application '{application}'...")
            filepath = service.generate_customized_resume(application)
        typer.echo(f"✅ Resume saved to: {filepath}")
    else:
        typer.echo("Generating general resume...")
        filepath = service.generate_general_resume()
        typer.echo(f"✅ Resume saved to: {filepath}")

    # Get token usage
    total_tokens = MeteredAIProvider.get_total_tokens()
    input_tokens = MeteredAIProvider.get_input_tokens()
    output_tokens = MeteredAIProvider.get_output_tokens()

    # Display token usage
    if total_tokens > 0:
        typer.echo("\n📊 Token Usage:")
        typer.echo(f"   Input tokens: {input_tokens:,}")
        typer.echo(f"   Output tokens: {output_tokens:,}")
        typer.echo(f"   Total tokens: {total_tokens:,}")
