"""Export command for converting resumes to PDF/Word."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import ExportService
from cveasy.cli_utils import (
    handle_errors,
    show_command_banner,
    with_spinner,
    show_success,
    prompt_select_application,
    GENERAL_RESUME_CHOICE,
)

app = typer.Typer(
    help="Export resumes to PDF or Word documents",
)


@app.callback(invoke_without_command=True)
@handle_errors
def export(
    format: str = typer.Option("pdf", "--format", help="Export format: pdf or docx"),
    output: Optional[str] = typer.Option(None, "--output", help="Output file path"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
    application: Optional[str] = typer.Option(
        None, "--application", "-a", help="Application ID to export resume for"
    ),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to resume markdown file"),
    select: bool = typer.Option(
        False, "--select", "-s", help="Prompt to select an application or general resume"
    ),
):
    """
    Export resume to PDF or Word document.

    You must specify exactly one source:
    - Use --application to export an application's resume
    - Use --file to specify a file path

    If neither --application nor --file is provided, prompts to select when run interactively.
    Use --select to explicitly request the selection prompt.

    If --output is not specified, the output file will be saved next to the source file.
    """
    project_path = get_project_path(project)

    # When no source specified, prompt to select an application or general resume (when interactive)
    if application is None and file is None:
        application = prompt_select_application(project_path, include_general=True)

    service = ExportService(project_path)

    # Validate that exactly one source is provided
    if application is None and file is None:
        typer.echo(
            "Error: You must specify a resume source. Use --application or --file.", err=True
        )
        raise typer.Exit(1)
    elif application is not None and file is not None:
        typer.echo(
            "Error: You can only specify one resume source. Use either --application or --file.",
            err=True,
        )
        raise typer.Exit(1)

    # Determine output path
    if output:
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = project_path / output_path

        # Determine the correct extension based on format
        if format.lower() == "pdf":
            correct_ext = ".pdf"
        elif format.lower() == "docx":
            correct_ext = ".docx"
        else:
            typer.echo(f"Error: Unknown format '{format}'. Use 'pdf' or 'docx'.", err=True)
            raise typer.Exit(1)

        # Handle file extension
        if not output_path.suffix:
            output_path = output_path.with_suffix(correct_ext)
        elif output_path.suffix.lower() != correct_ext:
            output_path = output_path.with_suffix(correct_ext)
    else:
        output_path = None

    # Show banner
    show_command_banner("export")

    # Export
    with with_spinner(f"Converting resume to {format.upper()}..."):
        if application == GENERAL_RESUME_CHOICE:
            output_path = service.export_general_resume(output_path, format)
        elif application:
            output_path = service.export_application_resume(application, output_path, format)
        else:
            file_path = Path(file)
            if not file_path.is_absolute():
                file_path = project_path / file_path
            output_path = service.export_file_resume(file_path, output_path, format)

    show_success(f"Resume exported to: {output_path}")
