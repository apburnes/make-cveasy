"""Check command for resume quality analysis."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.config import get_project_path
from cveasy.storage import MarkdownStorage
from cveasy.analysis import ResumeChecker

app = typer.Typer(
    help="Check resume quality against job descriptions",
    no_args_is_help=True,
)


@app.command()
def check(
    application_id: str = typer.Argument(..., help="Application ID"),
    project: Optional[str] = typer.Option(None, "--project", help="Project directory path"),
):
    """
    Check resume quality against job description.

    Automatically generates resume if it doesn't exist, then performs quality check
    and saves check-report.md to the application directory.
    """
    project_path = get_project_path(project)
    storage = MarkdownStorage(project_path)

    # Check if resume exists
    resume_content = storage.load_resume(application_id=application_id)

    if not resume_content:
        typer.echo(f"Resume not found for application '{application_id}'. Generating it now...")
        # Generate resume first using the generator directly
        from cveasy.ai import ResumeGenerator
        from cveasy.models.job import Job

        job = storage.load_job(application_id)
        if not job:
            typer.echo(f"Error: Job application '{application_id}' not found.", err=True)
            raise typer.Exit(1)

        skills = storage.list_skills()
        experiences = storage.list_experiences()
        stories = storage.list_stories()
        links = storage.list_links()
        projects = storage.list_projects()

        generator = ResumeGenerator()
        resume_content = generator.generate_customized_resume(
            job,
            skills,
            experiences,
            stories,
            links,
            projects,
        )

        storage.save_resume(resume_content, application_id=application_id)
        typer.echo("✅ Resume generated")

    # Load job description
    job = storage.load_job(application_id)
    if not job:
        typer.echo(f"Error: Job application '{application_id}' not found.", err=True)
        raise typer.Exit(1)

    # Load skills for matching
    skills = storage.list_skills()

    # Run check
    typer.echo(f"Checking resume against job description...")
    checker = ResumeChecker()
    report = checker.check(resume_content, job, skills)

    # Save report
    filepath = storage.save_check_report(report, application_id)
    typer.echo(f"✅ Check report saved to: {filepath}")
    typer.echo(f"\n💡 Tip: Review the report and run 'cveasy generate --application {application_id} --update' to improve your resume")
