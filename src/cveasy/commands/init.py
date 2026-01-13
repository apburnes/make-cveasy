"""Init command to scaffold project structure."""

import subprocess
from pathlib import Path
from typing import Optional
import typer

# Create app for backward compatibility if needed
app = typer.Typer()


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
    if project:
        # If --project is specified, use that as the project path
        project_path = Path(project).resolve()
        if project_path.exists() and not project_path.is_dir():
            typer.echo(f"Error: {project_path} exists but is not a directory.", err=True)
            raise typer.Exit(1)
    else:
        # Otherwise, create directory with the specified name in current working directory
        project_path = Path.cwd() / name

    if project_path.exists():
        typer.echo(f"Error: Directory {project_path} already exists.", err=True)
        raise typer.Exit(1)

    # Create directory
    try:
        project_path.mkdir(parents=True, exist_ok=False)
        typer.echo(f"Created project directory: {project_path}")
    except OSError as e:
        typer.echo(f"Error: Could not create directory {project_path}: {e}", err=True)
        raise typer.Exit(1)

    # Initialize git
    try:
        subprocess.run(["git", "init"], cwd=project_path, check=True, capture_output=True)
        typer.echo("Initialized git repository")
    except (subprocess.CalledProcessError, FileNotFoundError):
        typer.echo("Warning: Could not initialize git repository (git not found)", err=True)

    # Create subdirectories
    subdirs = ["skills", "experiences", "stories", "links", "projects", "applications", "resume"]
    for subdir in subdirs:
        (project_path / subdir).mkdir(exist_ok=True)
        typer.echo(f"Created directory: {subdir}/")

    # Create README.md
    readme_content = """# CVEasy Resume Project

This project is managed using CVEasy, a CLI tool for managing resume data and generating customized resumes.

## Directory Structure

- `skills/` - Your skills and competencies
- `experiences/` - Work experience and positions
- `stories/` - Success stories and achievements
- `links/` - Professional links (LinkedIn, GitHub, etc.)
- `projects/` - Personal and professional projects
- `applications/` - Job applications with customized resumes
- `resume/` - General resume files

## Usage

### Adding Data

```bash
cveasy add skill --name "Python"
cveasy add experience --name "Software Engineer"
cveasy add story --name "Led Migration"
cveasy add link --name "LinkedIn" --description "Professional profile" --url "https://linkedin.com/in/username"
cveasy add project --name "E-commerce Platform" --description "Full-stack application"
cveasy add job --name "Software Engineer Position" --url "https://example.com/job"
```

### Generating Resumes

```bash
# General resume
cveasy generate

# Customized for a job application
cveasy generate --application software-engineer-20240115

# Update based on check report
cveasy generate --application software-engineer-20240115 --update
```

### Checking Resume Quality

```bash
cveasy check software-engineer-20240115
```

### Exporting Resumes

```bash
cveasy export applications/software-engineer-20240115/resume.md --format pdf
cveasy export resume/resume-20240115.md --format docx
```

## Configuration

Create a `.env` file in this directory with your AI API keys:

```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
CVEASY_AI_PROVIDER=openai
```

For more information, visit: https://github.com/yourusername/cveasy
"""

    readme_path = project_path / "README.md"
    readme_path.write_text(readme_content, encoding="utf-8")
    typer.echo("Created README.md")

    # Create .env.example
    env_example_content = """# AI Provider Configuration
# Set CVEASY_AI_PROVIDER to: openai, anthropic, or openrouter

CVEASY_AI_PROVIDER=openai

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# OpenRouter Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
"""

    env_example_path = project_path / ".env.example"
    env_example_path.write_text(env_example_content, encoding="utf-8")
    typer.echo("Created .env.example")

    typer.echo(f"\n✅ Project initialized successfully at {project_path}")
    typer.echo(f"\nNext steps:")
    typer.echo(f"  1. cd {project_path}")
    typer.echo(f"  2. Copy .env.example to .env and add your API keys")
    typer.echo(f"  3. Start adding your resume data with 'cveasy add' commands")


# Also register as a command in the app for backward compatibility
app.command()(init)
