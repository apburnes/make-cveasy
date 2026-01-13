"""Import command for parsing resumes from PDF/DOCX files."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.storage import MarkdownStorage
from cveasy.parsing import (
    extract_text_from_pdf,
    extract_text_from_docx,
    parse_resume_with_llm,
    create_models_from_parsed_data,
)
from cveasy.ai.providers import get_ai_provider
from cveasy.models.link import Link

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

    storage = MarkdownStorage(project_path)

    # Resolve file path
    file_path = Path(file)
    if not file_path.is_absolute():
        file_path = Path.cwd() / file_path

    if not file_path.exists():
        typer.echo(f"Error: File not found: {file_path}", err=True)
        raise typer.Exit(1)

    # Detect file type
    file_ext = file_path.suffix.lower()
    if file_ext not in [".pdf", ".docx"]:
        typer.echo(f"Error: Unsupported file type '{file_ext}'. Only PDF and DOCX files are supported.", err=True)
        raise typer.Exit(1)

    # Extract text
    typer.echo(f"Extracting text from {file_path.name}...")
    try:
        if file_ext == ".pdf":
            text = extract_text_from_pdf(file_path)
        else:
            text = extract_text_from_docx(file_path)
    except Exception as e:
        typer.echo(f"Error: Failed to extract text from file: {e}", err=True)
        raise typer.Exit(1)

    if not text.strip():
        typer.echo("Error: No text could be extracted from the file.", err=True)
        raise typer.Exit(1)

    # Parse with LLM
    typer.echo("Parsing resume with AI...")
    try:
        provider = get_ai_provider()
        parsed_data = parse_resume_with_llm(text, provider)
    except Exception as e:
        typer.echo(f"Error: Failed to parse resume: {e}", err=True)
        raise typer.Exit(1)

    # Create model objects
    try:
        bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)
    except Exception as e:
        typer.echo(f"Error: Failed to create models from parsed data: {e}", err=True)
        raise typer.Exit(1)

    # Import statistics
    imported_bio = 0
    updated_bio = 0
    imported_skills = 0
    skipped_skills = 0
    imported_experiences = 0
    skipped_experiences = 0
    imported_projects = 0
    skipped_projects = 0
    imported_stories = 0
    skipped_stories = 0
    imported_educations = 0
    skipped_educations = 0
    imported_links = 0
    skipped_links = 0

    # Save bio (always update if bio exists in parsed data)
    if bio:
        existing = storage.load_bio()
        if existing:
            storage.save_bio(bio)
            updated_bio += 1
        else:
            storage.save_bio(bio)
            imported_bio += 1

    # Save skills
    for skill in skills:
        existing = storage.load_skill(skill.name)
        if existing:
            skipped_skills += 1
        else:
            storage.save_skill(skill)
            imported_skills += 1

    # Save experiences
    for experience in experiences:
        existing = storage.load_experience(experience.title)
        if existing:
            skipped_experiences += 1
        else:
            storage.save_experience(experience)
            imported_experiences += 1

    # Save projects
    for project in projects:
        existing = storage.load_project(project.name)
        if existing:
            skipped_projects += 1
        else:
            storage.save_project(project)
            imported_projects += 1

    # Save stories
    for story in stories:
        existing = storage.load_story(story.title)
        if existing:
            skipped_stories += 1
        else:
            storage.save_story(story)
            imported_stories += 1

    # Save educations
    for education in educations:
        existing = storage.load_education(education.name)
        if existing:
            skipped_educations += 1
        else:
            storage.save_education(education)
            imported_educations += 1

    # Save links
    for link in links:
        existing = storage.load_link(link.name)
        if existing:
            skipped_links += 1
        else:
            storage.save_link(link)
            imported_links += 1

    # Print summary
    typer.echo("\n✅ Import complete!")
    if bio:
        if updated_bio > 0:
            typer.echo(f"Bio: {imported_bio} imported, {updated_bio} updated")
        else:
            typer.echo(f"Bio: {imported_bio} imported")
    typer.echo(f"Skills: {imported_skills} imported, {skipped_skills} skipped")
    typer.echo(f"Experiences: {imported_experiences} imported, {skipped_experiences} skipped")
    typer.echo(f"Projects: {imported_projects} imported, {skipped_projects} skipped")
    typer.echo(f"Stories: {imported_stories} imported, {skipped_stories} skipped")
    typer.echo(f"Education: {imported_educations} imported, {skipped_educations} skipped")
    typer.echo(f"Links: {imported_links} imported, {skipped_links} skipped")

    total_imported = imported_bio + imported_skills + imported_experiences + imported_projects + imported_stories + imported_educations + imported_links
    if total_imported == 0:
        typer.echo("\n⚠️  No new entries were imported. All items may already exist or the resume may be empty.", err=True)
