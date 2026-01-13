"""Main CLI entry point for CVEasy."""

import typer
from cveasy.commands.init import init
from cveasy.commands import add, generate, check, export

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
  • Scrape job descriptions from URLs
  • Track multiple job applications with custom resumes

Commands:
  init      Initialize a new CVEasy project
  add       Add resume data (skills, experiences, stories, links, projects, jobs)
  generate  Generate resumes (general or customized for job applications)
  check     Check resume quality against job descriptions
  export    Export resumes to PDF or Word format

Use 'cveasy <command> --help' or 'cveasy <command> -h' for more information on a specific command.
""",
    add_completion=False,
    no_args_is_help=True,
)

# Add init command directly (not as a sub-app)
app.command()(init)

# Add command groups for other commands
app.add_typer(add.app, name="add")
app.add_typer(generate.app, name="generate")
app.add_typer(check.app, name="check")
app.add_typer(export.app, name="export")


def main():
    """
    Main entry point for CVEasy CLI.

    Run with --help or -h to see available commands.
    """
    app()


if __name__ == "__main__":
    main()
