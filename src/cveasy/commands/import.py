"""Import command for parsing resumes from PDF/DOCX files."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import ImportService
from cveasy.cli_utils import handle_errors


@handle_errors
def import_resume(
    file: str = typer.Option(..., "-f", "--file", help="Path to PDF or DOCX resume file"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Import resume data from a PDF or DOCX file.

    This command extracts text from the resume file, uses an LLM to parse it,
    and automatically creates skills, experiences, projects, stories, education, and links.
    Existing entries with the same name will be skipped (not overwritten).

    Examples:
        cveasy import -f resume.pdf
        cveasy import --file resume.docx
    """
    project_path = get_project_path(project)

    # Load .env file from project directory if it exists
    env_file = project_path / ".env"
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
        except ImportError:
            pass  # python-dotenv not installed, skip

    # Resolve file path
    file_path = Path(file)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    typer.echo(f"Extracting text from {file_path.name}...")
    typer.echo("Parsing resume with AI...")

    service = ImportService(project_path)
    stats = service.import_resume(file_path)

    # Print summary
    typer.echo("\n✅ Import complete!")
    if stats["imported_bio"] > 0 or stats["updated_bio"] > 0:
        if stats["updated_bio"] > 0:
            typer.echo(f"Bio: {stats['imported_bio']} imported, {stats['updated_bio']} updated")
        else:
            typer.echo(f"Bio: {stats['imported_bio']} imported")
    typer.echo(f"Skills: {stats['imported_skills']} imported, {stats['skipped_skills']} skipped")
    typer.echo(f"Experiences: {stats['imported_experiences']} imported, {stats['skipped_experiences']} skipped")
    typer.echo(f"Projects: {stats['imported_projects']} imported, {stats['skipped_projects']} skipped")
    typer.echo(f"Stories: {stats['imported_stories']} imported, {stats['skipped_stories']} skipped")
    typer.echo(f"Education: {stats['imported_educations']} imported, {stats['skipped_educations']} skipped")
    typer.echo(f"Links: {stats['imported_links']} imported, {stats['skipped_links']} skipped")

    total_imported = (
        stats["imported_bio"]
        + stats["imported_skills"]
        + stats["imported_experiences"]
        + stats["imported_projects"]
        + stats["imported_stories"]
        + stats["imported_educations"]
        + stats["imported_links"]
    )
    if total_imported == 0:
        typer.echo(
            "\n⚠️  No new entries were imported. All items may already exist or the resume may be empty.",
            err=True,
        )
