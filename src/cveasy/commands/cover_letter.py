"""Cover letter command for creating cover letters."""

from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import CoverLetterService
from cveasy.cli_utils import handle_errors, show_command_banner, with_spinner, show_success, show_info
from cveasy.ai.metered_provider import MeteredAIProvider

app = typer.Typer(
    help="Generate cover letters using AI",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
@handle_errors
def cover_letter(
    application: str = typer.Option(
        ..., "--application", "-a", help="Application ID to generate cover letter for"
    ),
    reason: Optional[str] = typer.Option(
        None, "--reason", "-r", help="Reason for interest in the job application"
    ),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project directory path"),
):
    """
    Generate a personalized cover letter for a job application.

    The cover letter is generated based on your skills, stories, experience,
    education, and projects, tailored to the specific job application.

    Use --reason to include a specific reason for your interest in the position.

    Examples:
        cveasy cover-letter --application software-engineer-20240115
        cveasy cover-letter -a software-engineer-20240115 --reason "I'm excited about the company's mission"
        cveasy cover-letter -a software-engineer-20240115 -r "I'm excited about the company's mission"
    """
    project_path = get_project_path(project)
    service = CoverLetterService(project_path)

    # Show banner
    show_command_banner("cover-letter")

    # Reset token counter before starting
    MeteredAIProvider.reset_total_tokens()

    with with_spinner(f"Crafting personalized cover letter for application '{application}'..."):
        filepath = service.generate_cover_letter(application, reason=reason)
    show_success(f"Cover letter saved to: {filepath}")

    # Get token usage
    total_tokens = MeteredAIProvider.get_total_tokens()
    input_tokens = MeteredAIProvider.get_input_tokens()
    output_tokens = MeteredAIProvider.get_output_tokens()

    # Display token usage
    if total_tokens > 0:
        show_info("\n# Token Usage:")
        typer.echo(f"   Input tokens: {input_tokens:,}")
        typer.echo(f"   Output tokens: {output_tokens:,}")
        typer.echo(f"   Total tokens: {total_tokens:,}")
