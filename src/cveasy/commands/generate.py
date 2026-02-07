"""Generate command for creating resumes."""

from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import ResumeService
from cveasy.cli_utils import (
    handle_errors,
    show_command_banner,
    with_spinner,
    show_success,
    show_info,
    prompt_select_application,
    GENERAL_RESUME_CHOICE,
)
from cveasy.ai.metered_provider import MeteredAIProvider

app = typer.Typer(
    help="Generate resumes using AI",
    no_args_is_help=False,
)


@app.callback(invoke_without_command=True)
@handle_errors
def generate(
    application: Optional[str] = typer.Option(
        None, "--application", "-a", help="Application ID to generate customized resume for"
    ),
    update: bool = typer.Option(
        False, "--update", "-u", help="Update resume from check report (use with an application: select one or use --application)"
    ),
    select: bool = typer.Option(
        True, "--select/--no-select", "-s", help="Prompt to select an application (default). Use --no-select to generate a general resume."
    ),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project directory path"),
):
    """
    Generate a resume.

    By default, prompts to select an application and generates a customized resume for it.
    Use --no-select to generate a general resume from all available data instead.
    Use --application to generate for a specific application without prompting.

    Use --update to improve the resume from the check report. This works when an
    application is chosen (via the select prompt or --application).

    Examples:
        cveasy generate
        cveasy generate --select
        cveasy generate --update
        cveasy generate --no-select
        cveasy generate --application software-engineer-20240115
        cveasy generate --application software-engineer-20240115 --update
    """
    project_path = get_project_path(project)
    service = ResumeService(project_path)

    # If --select and no --application, prompt to choose an application or general resume
    if application is None and select:
        application = prompt_select_application(project_path, include_general=True)
        if application is None:
            raise typer.Exit(1)
        if application == GENERAL_RESUME_CHOICE:
            application = None

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
        show_info("\n# Token Usage:")
        typer.echo(f"   Input tokens: {input_tokens:,}")
        typer.echo(f"   Output tokens: {output_tokens:,}")
        typer.echo(f"   Total tokens: {total_tokens:,}")
