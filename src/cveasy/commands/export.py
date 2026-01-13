"""Export command for converting resumes to PDF/Word."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.export import export_to_pdf, export_to_word
from cveasy.storage import MarkdownStorage

app = typer.Typer(
    help="Export resumes to PDF or Word documents",
)


@app.callback(invoke_without_command=True)
def export(
    format: str = typer.Option("pdf", "--format", help="Export format: pdf or docx"),
    output: Optional[str] = typer.Option(None, "--output", help="Output file path"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
    application: Optional[str] = typer.Option(None, "--application", "-a", help="Application ID to export resume for"),
    file: Optional[str] = typer.Option(None, "--file", "-f", help="Path to resume markdown file"),
):
    """
    Export resume to PDF or Word document.

    You must specify exactly one source:
    - Use --application to export an application's resume
    - Use --file to specify a file path

    If --output is not specified, the output file will be saved next to the source file.
    """
    project_path = get_project_path(project)

    # Validate that exactly one source is provided
    if application is None and file is None:
        typer.echo("Error: You must specify a resume source. Use --application or --file.", err=True)
        raise typer.Exit(1)
    elif application is not None and file is not None:
        typer.echo("Error: You can only specify one resume source. Use either --application or --file.", err=True)
        raise typer.Exit(1)

    # Determine resume content and source path
    if application:
        # Load resume from application
        storage = MarkdownStorage(project_path)
        resume_content = storage.load_resume(application_id=application)

        if not resume_content:
            typer.echo(f"Error: Resume not found for application '{application}'.", err=True)
            raise typer.Exit(1)

        # Determine source path for output calculation
        resume_path = project_path / "applications" / application / "resume.md"
    else:
        # Use --file flag
        resume_path = Path(file)
        if not resume_path.is_absolute():
            resume_path = project_path / resume_path

        if not resume_path.exists():
            typer.echo(f"Error: Resume file not found: {resume_path}", err=True)
            raise typer.Exit(1)

        # Read resume content
        with open(resume_path, "r", encoding="utf-8") as f:
            resume_content = f.read()

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
            # No extension provided, append the format extension
            output_path = output_path.with_suffix(correct_ext)
        elif output_path.suffix.lower() != correct_ext:
            # Incorrect extension provided, replace with correct one
            output_path = output_path.with_suffix(correct_ext)
        # If extension is already correct, use it as-is
    else:
        # Save next to source file with appropriate extension
        if format.lower() == "pdf":
            output_path = resume_path.with_suffix(".pdf")
        elif format.lower() == "docx":
            output_path = resume_path.with_suffix(".docx")
        else:
            typer.echo(f"Error: Unknown format '{format}'. Use 'pdf' or 'docx'.", err=True)
            raise typer.Exit(1)

    # Export
    typer.echo(f"Exporting resume to {format.upper()}...")

    if format.lower() == "pdf":
        export_to_pdf(resume_content, output_path)
    elif format.lower() == "docx":
        export_to_word(resume_content, output_path)
    else:
        typer.echo(f"Error: Unknown format '{format}'. Use 'pdf' or 'docx'.", err=True)
        raise typer.Exit(1)

    typer.echo(f"✅ Resume exported to: {output_path}")
