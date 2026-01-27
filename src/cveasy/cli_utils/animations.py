"""Animation and visual feedback utilities for CLI commands."""

import sys
from contextlib import contextmanager
from typing import Optional

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.panel import Panel
from rich import box

# Global console instance
console = Console()

# ASCII Art Banners
CVEASY_LOGO = """
╔═══════════════════════════════════════╗
║                                       ║
║     ╔═╗╦  ╔═╗╔═╗╔═╗╦ ╦╔═╗╦            ║
║     ║ ╦║  ║╣ ╠═╣╠═╝╠═╣║╣ ║            ║
║     ╚═╝╩═╝╚═╝╩ ╩╩  ╩ ╩╚═╝╩═╝          ║
║                                       ║
║     Make Your Resume Easy             ║
║                                       ║
╚═══════════════════════════════════════╝
"""

BANNERS = {
    "generate": """
╔═══════════════════════════════════════╗
║    🚀 Generating Resume               ║
╚═══════════════════════════════════════╝
""",
    "check": """
╔═══════════════════════════════════════╗
║    🔍 Checking Resume Quality        ║
╚═══════════════════════════════════════╝
""",
    "import": """
╔═══════════════════════════════════════╗
║    📥 Importing Resume                ║
╚═══════════════════════════════════════╝
""",
    "export": """
╔═══════════════════════════════════════╗
║    📤 Exporting Resume                ║
╚═══════════════════════════════════════╝
""",
    "cover-letter": """
╔═══════════════════════════════════════╗
║    ✉️  Generating Cover Letter        ║
╚═══════════════════════════════════════╝
""",
    "add": """
╔═══════════════════════════════════════╗
║    ➕ Adding Resume Data              ║
╚═══════════════════════════════════════╝
""",
    "init": """
╔═══════════════════════════════════════╗
║    🎯 Initializing CVEasy Project     ║
╚═══════════════════════════════════════╝
""",
    "config": """
╔═══════════════════════════════════════╗
║    ⚙️  Configuring CVEasy             ║
╚═══════════════════════════════════════╝
""",
}


def should_show_animations() -> bool:
    """Check if animations should be shown (not in quiet mode or non-interactive terminal)."""
    # Check if output is being redirected
    if not sys.stdout.isatty():
        return False
    # Check for NO_COLOR environment variable
    import os
    if os.environ.get("NO_COLOR") or os.environ.get("CVEASY_NO_ANIMATIONS"):
        return False
    return True


def show_banner(banner_type: Optional[str] = None, quiet: bool = False):
    """
    Display ASCII art banner.

    Args:
        banner_type: Type of banner to show (e.g., 'generate', 'check', 'import')
                    If None, shows main CVEasy logo
        quiet: If True, skip banner display
    """
    if quiet or not should_show_animations():
        return

    if banner_type:
        banner = BANNERS.get(banner_type, "")
        if banner:
            console.print(banner, style="bold cyan")
    else:
        console.print(CVEASY_LOGO, style="bold cyan")


def show_command_banner(command_name: str, quiet: bool = False):
    """
    Display command-specific banner.

    Args:
        command_name: Name of the command
        quiet: If True, skip banner display
    """
    show_banner(command_name, quiet=quiet)


@contextmanager
def with_spinner(message: str, style: str = "cyan"):
    """
    Context manager for spinner animation.

    Args:
        message: Message to display with spinner
        style: Rich style for the spinner

    Example:
        with with_spinner("Processing..."):
            do_work()
    """
    if should_show_animations():
        with console.status(f"[{style}]{message}[/{style}]", spinner="dots"):
            yield
    else:
        # Fallback for non-interactive terminals
        console.print(f"[{style}]{message}[/{style}]")
        yield


@contextmanager
def with_progress_bar(total: int, description: str = "Processing"):
    """
    Context manager for progress bar.

    Args:
        total: Total number of steps
        description: Description of the progress

    Example:
        with with_progress_bar(10, "Importing data") as progress:
            for i in range(10):
                progress.update(1)
                do_work()
    """
    if should_show_animations():
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            console=console,
        ) as progress:
            progress.add_task(description, total=total)
            yield progress
    else:
        # Fallback for non-interactive terminals
        console.print(f"[cyan]{description}[/cyan]")
        yield None


def show_step(message: str, status: str = "info"):
    """
    Display a step with status icon.

    Args:
        message: Step message
        status: Status type ('info', 'success', 'warning', 'error')
    """
    icons = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌",
    }
    styles = {
        "info": "cyan",
        "success": "green",
        "warning": "yellow",
        "error": "red",
    }
    icon = icons.get(status, "•")
    style = styles.get(status, "white")
    console.print(f"[{style}]{icon} {message}[/{style}]")


def show_success(message: str):
    """Display success message with styling."""
    console.print(f"[bold green]✅ {message}[/bold green]")


def show_info(message: str):
    """Display info message with styling."""
    console.print(f"[cyan]ℹ️  {message}[/cyan]")


def show_warning(message: str):
    """Display warning message with styling."""
    console.print(f"[yellow]⚠️  {message}[/yellow]")


def show_error(message: str):
    """Display error message with styling."""
    console.print(f"[bold red]❌ {message}[/bold red]", file=sys.stderr)


def show_panel(content: str, title: str = "", border_style: str = "cyan"):
    """
    Display content in a styled panel.

    Args:
        content: Content to display
        title: Panel title
        border_style: Rich style for the border
    """
    if should_show_animations():
        console.print(Panel(content, title=title, border_style=border_style, box=box.ROUNDED))
    else:
        if title:
            console.print(f"{title}:")
        console.print(content)
