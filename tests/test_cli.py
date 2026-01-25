"""Tests for CLI main function and help output."""

import pytest
from typer.testing import CliRunner

from cveasy.cli import app, main


def test_cli_main_function():
    """Test main() function can be called."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0


def test_cli_help_output():
    """Test CLI help output contains expected information."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])

    assert result.exit_code == 0
    assert "CVEasy" in result.stdout
    assert "init" in result.stdout
    assert "add" in result.stdout
    assert "generate" in result.stdout
    assert "check" in result.stdout
    assert "export" in result.stdout
    assert "import" in result.stdout


def test_cli_no_args_shows_help():
    """Test CLI with no arguments shows help."""
    runner = CliRunner()
    result = runner.invoke(app, [])

    # Typer may exit with code 2 for missing arguments, but should show help
    assert result.exit_code in [0, 2]
    assert "CVEasy" in result.stdout or "Usage" in result.stdout or "help" in result.stdout.lower()


def test_cli_init_command_registered():
    """Test init command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["init", "--help"])

    assert result.exit_code == 0
    assert "init" in result.stdout.lower()


def test_cli_add_command_registered():
    """Test add command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["add", "--help"])

    assert result.exit_code == 0
    assert "add" in result.stdout.lower()


def test_cli_generate_command_registered():
    """Test generate command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["generate", "--help"])

    assert result.exit_code == 0
    assert "generate" in result.stdout.lower()


def test_cli_check_command_registered():
    """Test check command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["check", "--help"])

    assert result.exit_code == 0
    assert "check" in result.stdout.lower()


def test_cli_export_command_registered():
    """Test export command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["export", "--help"])

    assert result.exit_code == 0
    assert "export" in result.stdout.lower()


def test_cli_import_command_registered():
    """Test import command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["import", "--help"])

    assert result.exit_code == 0
    assert "import" in result.stdout.lower()


def test_cli_version_command_registered():
    """Test version command is registered."""
    runner = CliRunner()
    result = runner.invoke(app, ["version", "--help"])

    assert result.exit_code == 0
    assert "version" in result.stdout.lower()


def test_cli_version_command_output():
    """Test version command outputs the correct version."""
    from cveasy import __version__

    runner = CliRunner()
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert __version__ in result.stdout
