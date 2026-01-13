"""Generate command for creating resumes."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.storage import MarkdownStorage
from cveasy.ai import ResumeGenerator

app = typer.Typer(
    help="Generate resumes using AI",
    no_args_is_help=True,
)


@app.callback(invoke_without_command=True)
def generate(
    application: Optional[str] = typer.Option(None, "--application", "-a", help="Application ID to generate customized resume for"),
    update: bool = typer.Option(False, "--update", "-u", help="Update resume based on check report (requires --application)"),
    project: Optional[str] = typer.Option(None, "--project", "-p", help="Project directory path"),
):
    """
    Generate a resume.

    If --application is specified, generates a customized resume for that job application.
    Otherwise, generates a general resume from all available data.

    Use --update flag with --application to improve resume based on check report.

    Examples:
        cveasy generate
        cveasy generate --application software-engineer-20240115
        cveasy generate --application software-engineer-20240115 --update
    """
    project_path = get_project_path(project)
    storage = MarkdownStorage(project_path)

    # Load all resume data
    bio = storage.load_bio()
    skills = storage.list_skills()
    experiences = storage.list_experiences()
    stories = storage.list_stories()
    links = storage.list_links()
    projects = storage.list_projects()
    educations = storage.list_educations()

    generator = ResumeGenerator()

    if application:
        # Load job description
        job = storage.load_job(application)
        if not job:
            typer.echo(f"Error: Job application '{application}' not found.", err=True)
            raise typer.Exit(1)

        if update:
            # Load current resume and check report
            current_resume = storage.load_resume(application_id=application)
            if not current_resume:
                typer.echo(f"Error: No resume found for application '{application}'. Generate it first.", err=True)
                raise typer.Exit(1)

            check_report = storage.load_check_report(application)
            if not check_report:
                typer.echo(f"Error: No check report found for application '{application}'. Run 'cveasy check' first.", err=True)
                raise typer.Exit(1)

            typer.echo(f"Updating resume for application '{application}' based on check report...")
            resume_content = generator.update_resume_from_check_report(
                current_resume,
                check_report,
                job,
                skills,
                experiences,
                stories,
                links,
                projects,
                educations,
                bio,
            )
        else:
            typer.echo(f"Generating customized resume for application '{application}'...")
            resume_content = generator.generate_customized_resume(
                job,
                skills,
                experiences,
                stories,
                links,
                projects,
                educations,
                bio,
            )

        filepath = storage.save_resume(resume_content, application_id=application)
        typer.echo(f"✅ Resume saved to: {filepath}")
    else:
        typer.echo("Generating general resume...")
        resume_content = generator.generate_general_resume(
            skills,
            experiences,
            stories,
            links,
            projects,
            educations,
            bio,
        )

        filepath = storage.save_resume(resume_content)
        typer.echo(f"✅ Resume saved to: {filepath}")
