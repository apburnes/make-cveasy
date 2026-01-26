"""Main CLI entry point for CVEasy."""

import typer
import importlib

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

# Track if commands have been registered
_commands_registered = False


def _register_commands():
    """Register all commands lazily."""
    global _commands_registered
    if _commands_registered:
        return

    # Import and register simple commands
    # These modules are lightweight (just function definitions)
    from cveasy.commands.init import init
    from cveasy.commands.config import config
    from cveasy.commands.version import version

    import_cmd = importlib.import_module("cveasy.commands.import")

    app.command()(init)
    app.command(name="config")(config)
    app.command(name="version")(version)
    app.command(name="import")(import_cmd.import_resume)

    # Register command groups
    # These modules are also lightweight (just Typer app definitions)
    # Heavy dependencies (services, AI providers) are only loaded when commands are invoked
    add_module = importlib.import_module("cveasy.commands.add")
    generate_module = importlib.import_module("cveasy.commands.generate")
    check_module = importlib.import_module("cveasy.commands.check")
    export_module = importlib.import_module("cveasy.commands.export")
    cover_letter_module = importlib.import_module("cveasy.commands.cover_letter")

    app.add_typer(add_module.app, name="add")
    app.add_typer(generate_module.app, name="generate")
    app.add_typer(check_module.app, name="check")
    app.add_typer(export_module.app, name="export")
    app.add_typer(cover_letter_module.app, name="cover-letter")

    _commands_registered = True


# Register commands on module import to ensure they're available for testing
# Command modules are imported here, but their heavy dependencies (services, AI providers)
# are only loaded when commands are actually invoked, not when modules are imported
_register_commands()


def main():
    """
    Main entry point for CVEasy CLI.

    Run with --help or -h to see available commands.
    """
    app()


if __name__ == "__main__":
    main()
