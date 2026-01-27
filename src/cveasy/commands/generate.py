"""Generate command for creating resumes."""

from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import ResumeService
from cveasy.cli_utils import handle_errors, show_command_banner, with_spinner, show_success, show_info
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

    # Show banner
    show_command_banner("generate")

    # Reset token counter before starting
    MeteredAIProvider.reset_total_tokens()

    if application:
        if update:
            with with_spinner("Analyzing check report and updating resume..."):
                filepath = service.update_resume_from_check_report(application)
            show_success(f"Resume updated and saved to: {filepath}")
        else:
            with with_spinner("Crafting your customized resume with AI..."):
                filepath = service.generate_customized_resume(application)
            show_success(f"Resume saved to: {filepath}")
    else:
        with with_spinner("Crafting your general resume with AI..."):
            filepath = service.generate_general_resume()
        show_success(f"Resume saved to: {filepath}")

    # Get token usage
    total_tokens = MeteredAIProvider.get_total_tokens()
    input_tokens = MeteredAIProvider.get_input_tokens()
    output_tokens = MeteredAIProvider.get_output_tokens()

    # Display token usage
    if total_tokens > 0:
        show_info("\n📊 Token Usage:")
        typer.echo(f"   Input tokens: {input_tokens:,}")
        typer.echo(f"   Output tokens: {output_tokens:,}")
        typer.echo(f"   Total tokens: {total_tokens:,}")
