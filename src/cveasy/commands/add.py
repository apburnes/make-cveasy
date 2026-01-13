"""Add command for creating resume data entries."""

from datetime import datetime
from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.storage import MarkdownStorage
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.story import Story
from cveasy.models.link import Link
from cveasy.models.project import Project
from cveasy.models.job import Job
from cveasy.models.education import Education
from cveasy.models.bio import Bio
from cveasy.scraping import JobScraper

app = typer.Typer(
    help="Add resume data entries",
    no_args_is_help=True,
)


@app.command()
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
    storage = MarkdownStorage(project_path)

    skill_obj = Skill(
        name=name,
        category=None,
        years=None,
        proficiency=None,
        related_experience=[],
        content="",
    )

    filepath = storage.save_skill(skill_obj)
    typer.echo(f"✅ Created skill: {filepath}")
    typer.echo(f"   Edit the file to add category, years, proficiency, and description")


@app.command()
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
    storage = MarkdownStorage(project_path)

    experience_obj = Experience(
        title=name,
        organization="",
        start_date=None,
        end_date=None,
        location=None,
        related_skills=[],
        related_stories=[],
        content="",
    )

    filepath = storage.save_experience(experience_obj)
    typer.echo(f"✅ Created experience: {filepath}")
    typer.echo(f"   Edit the file to add organization, dates, location, and description")


@app.command()
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
    storage = MarkdownStorage(project_path)

    story_obj = Story(
        title=name,
        context=None,
        outcome=None,
        content="",
    )

    filepath = storage.save_story(story_obj)
    typer.echo(f"✅ Created story: {filepath}")
    typer.echo(f"   Edit the file to add context, outcome, and detailed description")


@app.command()
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
    storage = MarkdownStorage(project_path)

    link_obj = Link(
        name=name,
        description=description,
        url=url,
    )

    filepath = storage.save_link(link_obj)
    typer.echo(f"✅ Created link: {filepath}")


@app.command()
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
    storage = MarkdownStorage(project_path)

    project_obj = Project(
        name=name,
        description=description,
        link=link,
        content="",
    )

    filepath = storage.save_project(project_obj)
    typer.echo(f"✅ Created project: {filepath}")
    typer.echo(f"   Edit the file to add detailed project summary")


@app.command()
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
    storage = MarkdownStorage(project_path)

    education_obj = Education(
        name=name,
        start_date=start_date,
        end_date=end_date,
        degree=degree,
        certificate=certificate,
        organization=organization,
        content="",
    )

    filepath = storage.save_education(education_obj)
    typer.echo(f"✅ Created education: {filepath}")
    typer.echo(f"   Edit the file to add additional description")


@app.command()
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
    storage = MarkdownStorage(project_path)

    bio_obj = Bio(
        name=name,
        location=location or "",
    )

    filepath = storage.save_bio(bio_obj)
    typer.echo(f"✅ Created/updated bio: {filepath}")


@app.command()
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
    from slugify import slugify

    project_path = get_project_path(project)
    storage = MarkdownStorage(project_path)

    # Create application ID with date
    date_str = datetime.now().strftime("%Y%m%d")
    slugified_name = slugify(name, lowercase=True)
    application_id = f"{slugified_name}-{date_str}"

    if url:
        # Scrape job description
        typer.echo(f"Scraping job description from {url}...")
        scraper = JobScraper()
        job_obj = scraper.scrape(url)

        if not job_obj:
            typer.echo("Warning: Could not scrape job description. Creating empty job entry.", err=True)
            job_obj = Job(
                name=name,
                title=None,
                location=None,
                requirements=None,
                pay=None,
                content="",
            )
        else:
            # Update name if not set
            if not job_obj.name or job_obj.name == "Job Application":
                job_obj.name = name
    else:
        # Create empty job entry
        job_obj = Job(
            name=name,
            title=None,
            location=None,
            requirements=None,
            pay=None,
            content="",
        )

    filepath = storage.save_job(job_obj, application_id)
    typer.echo(f"✅ Created job application: {filepath}")
    typer.echo(f"   Application ID: {application_id}")
    if not url:
        typer.echo(f"   Edit the file to add job description details")
