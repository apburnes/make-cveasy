"""Check command for resume quality analysis."""

from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import CheckService
from cveasy.cli_utils import (
    handle_errors,
    show_command_banner,
    with_spinner,
    show_success,
    show_info,
    prompt_select_application,
)
from cveasy.ai.metered_provider import MeteredAIProvider

app = typer.Typer(
    help="Check resume quality against job descriptions",
    no_args_is_help=False,
)


@app.callback(invoke_without_command=True)
@handle_errors
def check(
    application_id: Optional[str] = typer.Option(
        None, "-a", "--application", help="Application ID to run resume check for (prompts to select if omitted)"
    ),
    select: bool = typer.Option(
        False, "--select", "-s", help="Prompt to select an application interactively"
    ),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Check resume quality against job description.

    Automatically generates resume if it doesn't exist, then performs quality check
    and saves check-report.md to the application directory.

    If --application is omitted, prompts to select an application interactively.
    Use --select to explicitly request the selection prompt.

    Usage:
        cveasy check
        cveasy check --select
        cveasy check --application <application-id>
        cveasy check -a <application-id> --project /path/to/project
    """
    project_path = get_project_path(project)

    # If no application specified, prompt to choose one
    if application_id is None:
        application_id = prompt_select_application(project_path)
        if application_id is None:
            raise typer.Exit(1)

    service = CheckService(project_path)

    # Show banner
    show_command_banner("check")

    # Reset token counter before starting
    MeteredAIProvider.reset_total_tokens()

    with with_spinner("Generating quality report with AI..."):
        report, filepath = service.check_resume(application_id)

    # Get token usage
    total_tokens = MeteredAIProvider.get_total_tokens()
    input_tokens = MeteredAIProvider.get_input_tokens()
    output_tokens = MeteredAIProvider.get_output_tokens()

    show_success(f"Check report saved to: {filepath}")
    show_info(
        f"\n• Tip: Review the report and run 'cveasy generate --application {application_id} --update' to improve your resume"
    )

    # Display token usage
    if total_tokens > 0:
        show_info("\n# Token Usage:")
        typer.echo(f"   Input tokens: {input_tokens:,}")
        typer.echo(f"   Output tokens: {output_tokens:,}")
        typer.echo(f"   Total tokens: {total_tokens:,}")
