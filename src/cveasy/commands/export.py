"""Export command for converting resumes to PDF/Word."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.export import export_to_pdf, export_to_word

app = typer.Typer(
    help="Export resumes to PDF or Word documents",
    no_args_is_help=True,
)


@app.command()
def export(
    resume_file: str = typer.Argument(..., help="Path to resume markdown file"),
    format: str = typer.Option("pdf", "--format", help="Export format: pdf or docx"),
    output: Optional[str] = typer.Option(None, "--output", help="Output file path"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Export resume to PDF or Word document.

    The resume_file should be a path to a markdown resume file.
    If --output is not specified, the output file will be saved next to the source file.
    """
    project_path = get_project_path(project)

    # Resolve resume file path
    resume_path = Path(resume_file)
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
