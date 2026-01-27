"""Import command for parsing resumes from PDF/DOCX files."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import ImportService
from cveasy.cli_utils import handle_errors, show_command_banner, with_spinner, show_success, show_info, show_step
from cveasy.ai.metered_provider import MeteredAIProvider


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

    # Show banner
    show_command_banner("import")

    # Reset token counter before starting
    MeteredAIProvider.reset_total_tokens()

    service = ImportService(project_path)
    with with_spinner(f"Extracting text from {file_path.name} and parsing with AI..."):
        stats = service.import_resume(file_path)

    # Get token usage
    total_tokens = MeteredAIProvider.get_total_tokens()
    input_tokens = MeteredAIProvider.get_input_tokens()
    output_tokens = MeteredAIProvider.get_output_tokens()

    # Print summary
    show_success("\nImport complete!")
    if stats["imported_bio"] > 0 or stats["updated_bio"] > 0:
        if stats["updated_bio"] > 0:
            show_step(f"Bio: {stats['imported_bio']} imported, {stats['updated_bio']} updated", "success")
        else:
            show_step(f"Bio: {stats['imported_bio']} imported", "success")
    show_step(f"Skills: {stats['imported_skills']} imported, {stats['skipped_skills']} skipped", "success")
    show_step(
        f"Experiences: {stats['imported_experiences']} imported, {stats['skipped_experiences']} skipped",
        "success"
    )
    show_step(
        f"Projects: {stats['imported_projects']} imported, {stats['skipped_projects']} skipped",
        "success"
    )
    show_step(f"Stories: {stats['imported_stories']} imported, {stats['skipped_stories']} skipped", "success")
    show_step(
        f"Education: {stats['imported_educations']} imported, {stats['skipped_educations']} skipped",
        "success"
    )
    show_step(f"Links: {stats['imported_links']} imported, {stats['skipped_links']} skipped", "success")

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

    # Display token usage
    if total_tokens > 0:
        show_info("\n📊 Token Usage:")
        typer.echo(f"   Input tokens: {input_tokens:,}")
        typer.echo(f"   Output tokens: {output_tokens:,}")
        typer.echo(f"   Total tokens: {total_tokens:,}")
