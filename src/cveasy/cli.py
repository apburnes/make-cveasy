"""Main CLI entry point for CVEasy."""

import typer
import importlib
from cveasy.commands.init import init
from cveasy.commands.config import config
from cveasy.commands.version import version
from cveasy.commands import add, generate, check, export, cover_letter
# Import import command using importlib to avoid keyword conflict
import_cmd = importlib.import_module("cveasy.commands.import")

app = typer.Typer(
    name="cveasy",
    help="""CVEasy - CLI tool for managing resume data and generating customized resumes.

CVEasy helps you manage your resume data (skills, experiences, stories, links, projects)
and generate AI-powered customized resumes for job applications.

Key Features:
  • Manage resume data in markdown files with YAML frontmatter
  • Generate customized resumes using AI (OpenAI, Anthropic, OpenRouter)
  • Check resume quality against job descriptions
  • Export resumes to PDF or Word documents
  • Import resume data from PDF or DOCX files
  • Scrape job descriptions from URLs
  • Track multiple job applications with custom resumes

Commands:
  init         Initialize a new CVEasy project
  config       Configure environment variables interactively
  version      Display the current version of CVEasy
  add          Add resume data (skills, experiences, stories, links, projects, jobs)
  generate     Generate resumes (general or customized for job applications)
  cover-letter Generate personalized cover letters for job applications
  check        Check resume quality against job descriptions
  export       Export resumes to PDF or Word format
  import       Import resume data from PDF or DOCX files

Use 'cveasy <command> --help' or 'cveasy <command> -h' for more information on a specific command.
""",
    add_completion=False,
    no_args_is_help=True,
)

# Add init command directly (not as a sub-app)
app.command()(init)

# Add config command directly (not as a sub-app)
app.command(name="config")(config)

# Add version command directly (not as a sub-app)
app.command(name="version")(version)

# Add import command directly (not as a sub-app) to avoid keyword conflict
app.command(name="import")(import_cmd.import_resume)

# Add command groups for other commands
app.add_typer(add.app, name="add")
app.add_typer(generate.app, name="generate")
app.add_typer(check.app, name="check")
app.add_typer(export.app, name="export")
app.add_typer(cover_letter.app, name="cover-letter")


def main():
    """
    Main entry point for CVEasy CLI.

    Run with --help or -h to see available commands.
    """
    app()


if __name__ == "__main__":
    main()
