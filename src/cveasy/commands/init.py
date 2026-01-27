"""Init command to scaffold project structure."""

from pathlib import Path
from typing import Optional
import typer

from cveasy.services import ProjectService
from cveasy.cli_utils import handle_errors, show_command_banner, show_step, show_success

# Create app for backward compatibility if needed
app = typer.Typer()


@app.command()
@handle_errors
def init(
    name: str = typer.Option(
        "my-cveasy-resume",
        "-n",
        "--name",
        help="Name of the project directory to create. Defaults to 'my-cveasy-resume'.",
    ),
    project: Optional[str] = typer.Option(
        None,
        "--project",
        help="Path to the project directory. If not specified, creates the directory in the current working directory.",
    ),
):
    """
    Initialize a new CVEasy project.

    Use the -n or --name flag to specify a custom name for your project directory.
    If not specified, the project will be named 'my-cveasy-resume'.

    This command creates a new CVEasy project with the following structure:

    • Creates a project directory (use -n/--name to customize the name)
    • Initializes a git repository in the project directory
    • Creates required subdirectories: skills/, experiences/, stories/, links/, projects/, applications/, resume/
    • Creates a README.md with usage instructions
    • Creates a .env.example file for AI API key configuration
    • Creates a bio.md file for your name and location

    The project directory will be created in the current working directory unless --project is specified.

    Options:
        -n, --name TEXT    Name of the project directory (default: 'my-cveasy-resume')
        --project TEXT     Path to the project directory (optional)

    Examples:
        cveasy init
        cveasy init -n my-resume
        cveasy init --name professional-resume
        cveasy init -n my-resume --project /path/to/projects
    """
    # Show banner
    show_command_banner("init")

    project_path = Path(project).resolve() if project else None
    service = ProjectService()
    final_path = service.initialize_project(name, project_path)

    show_step(f"Created project directory: {final_path}", "success")
    show_step("Initialized git repository", "success")
    show_step("Created .gitignore", "success")
    show_step("Created directory: skills/", "success")
    show_step("Created directory: experiences/", "success")
    show_step("Created directory: stories/", "success")
    show_step("Created directory: links/", "success")
    show_step("Created directory: projects/", "success")
    show_step("Created directory: applications/", "success")
    show_step("Created directory: resume/", "success")
    show_step("Created directory: education/", "success")
    show_step("Created README.md", "success")
    show_step("Created .env.example", "success")
    show_step("Created bio.md", "success")

    show_success(f"\nProject initialized successfully at {final_path}")
    typer.echo("\nNext steps:")
    typer.echo(f"  1. cd {final_path}")
    typer.echo("  2. Copy .env.example to .env and add your API keys")
    typer.echo("  3. Import your resume with `cveasy import -f path/to/your/resume.pdf`")
    typer.echo("  4. Start adding to your resume data with 'cveasy add' commands")
