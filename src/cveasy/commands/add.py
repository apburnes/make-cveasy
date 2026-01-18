"""Add command for creating resume data entries."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.services import DataService, ApplicationService
from cveasy.cli_utils import handle_errors

app = typer.Typer(
    help="Add resume data entries",
    no_args_is_help=True,
)


@app.command()
@handle_errors
def skill(
    name: str = typer.Option(..., "--name", help="Skill name"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add a new skill.

    Creates a skill entry in the skills/ directory with frontmatter metadata.
    Edit the generated file to add category, years, proficiency, and description.
    """
    project_path = get_project_path(project)
    service = DataService(project_path)

    filepath = service.create_skill(name)
    typer.echo(f"✅ Created skill: {filepath}")
    typer.echo(f"   Edit the file to add category, years, proficiency, and description")


@app.command()
@handle_errors
def experience(
    name: str = typer.Option(..., "--name", help="Experience name/title"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add a new work experience.

    Creates an experience entry in the experiences/ directory.
    Edit the generated file to add organization, dates, location, and description.
    """
    project_path = get_project_path(project)
    service = DataService(project_path)

    filepath = service.create_experience(name)
    typer.echo(f"✅ Created experience: {filepath}")
    typer.echo(f"   Edit the file to add organization, dates, location, and description")


@app.command()
@handle_errors
def story(
    name: str = typer.Option(..., "--name", help="Story name/title"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add a new success story or achievement.

    Creates a story entry in the stories/ directory.
    Edit the generated file to add context, outcome, and detailed description.
    """
    project_path = get_project_path(project)
    service = DataService(project_path)

    filepath = service.create_story(name)
    typer.echo(f"✅ Created story: {filepath}")
    typer.echo(f"   Edit the file to add context, outcome, and detailed description")


@app.command()
@handle_errors
def link(
    name: str = typer.Option(..., "--name", help="Link name (e.g., LinkedIn, GitHub)"),
    description: str = typer.Option(..., "--description", help="Link description"),
    url: str = typer.Option(..., "--url", help="Link URL"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add a new professional link.

    Creates a link entry in the links/ directory (e.g., LinkedIn, GitHub, portfolio).
    All flags (--name, --description, --url) are required.
    """
    project_path = get_project_path(project)
    service = DataService(project_path)

    filepath = service.create_link(name, description, url)
    typer.echo(f"✅ Created link: {filepath}")


@app.command()
@handle_errors
def project(
    name: str = typer.Option(..., "--name", help="Project name"),
    description: str = typer.Option(..., "--description", help="Project description"),
    link: Optional[str] = typer.Option(None, "--link", help="Project URL (optional)"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add a new project.

    Creates a project entry in the projects/ directory.
    Edit the generated file to add detailed project summary.
    """
    project_path = get_project_path(project)
    service = DataService(project_path)

    filepath = service.create_project(name, description, link)
    typer.echo(f"✅ Created project: {filepath}")
    typer.echo(f"   Edit the file to add detailed project summary")


@app.command()
@handle_errors
def education(
    name: str = typer.Option(..., "--name", help="Education name/title"),
    start_date: Optional[str] = typer.Option(None, "--start_date", help="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, "--end_date", help="End date (YYYY-MM-DD) or 'Present'"),
    degree: Optional[str] = typer.Option(None, "--degree", help="Degree type (e.g., Bachelor of Science)"),
    certificate: Optional[str] = typer.Option(None, "--certificate", help="Certificate name"),
    organization: Optional[str] = typer.Option(None, "--organization", help="School/institution name"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add a new education entry.

    Creates an education entry in the education/ directory.
    Edit the generated file to add additional description.
    """
    project_path = get_project_path(project)
    service = DataService(project_path)

    filepath = service.create_education(name, start_date, end_date, degree, certificate, organization)
    typer.echo(f"✅ Created education: {filepath}")
    typer.echo(f"   Edit the file to add additional description")


@app.command()
@handle_errors
def bio(
    name: str = typer.Option(..., "--name", help="Your name"),
    location: Optional[str] = typer.Option(None, "--location", help="Your location (optional)"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add or update your bio information.

    Creates or updates a bio.md file with your name and optional location.
    This information will be used in resume generation.
    """
    project_path = get_project_path(project)
    service = DataService(project_path)

    filepath = service.create_or_update_bio(name, location)
    typer.echo(f"✅ Created/updated bio: {filepath}")


@app.command()
@handle_errors
def job(
    name: str = typer.Option(..., "--name", help="Job application name"),
    url: Optional[str] = typer.Option(None, "--url", help="URL to scrape job description from"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Add a new job application.

    Creates a job application directory in applications/ with a slugified name and date.
    If --url is provided, automatically scrapes job description from the URL.
    Otherwise, creates an empty job-description.md file for manual entry.
    """
    project_path = get_project_path(project)
    service = ApplicationService(project_path)

    if url:
        typer.echo(f"Scraping job description from {url}...")

    application_id, filepath = service.create_application(name, url)
    typer.echo(f"✅ Created job application: {filepath}")
    typer.echo(f"   Application ID: {application_id}")
    if not url:
        typer.echo(f"   Edit the file to add job description details")
