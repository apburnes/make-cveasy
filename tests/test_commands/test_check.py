"""Tests for check command."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cveasy.cli import app
from cveasy.models.job import Job
from cveasy.models.skill import Skill


def test_check_with_existing_resume(temp_dir, storage):
    """Test check command with existing resume."""
    runner = CliRunner()

    # Set up application with resume
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description here",
    )
    storage.save_job(job, application_id)
    storage.save_resume("# Resume\n\nContent here", application_id=application_id)
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content=""))

    mock_checker = MagicMock()
    mock_checker.check.return_value = "# Check Report\n\nAnalysis here"

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.check.ResumeChecker", return_value=mock_checker):
            result = runner.invoke(app, ["check", "--application", application_id])

            assert result.exit_code == 0
            assert "Checking resume against job description" in result.stdout
            assert "Check report saved to" in result.stdout

            # Verify checker was called
            mock_checker.check.assert_called_once()


def test_check_application_not_found(temp_dir, storage):
    """Test check command when application doesn't exist."""
    runner = CliRunner()

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["check", "--application", "nonexistent-app"])

        assert result.exit_code == 1
        assert "not found" in result.stdout


def test_check_job_not_found(temp_dir, storage):
    """Test check command when job doesn't exist (edge case)."""
    runner = CliRunner()

    application_id = "test-app-20240101"
    # Create application directory but no job file
    (temp_dir / "applications" / application_id).mkdir(parents=True)

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["check", "--application", application_id])

        assert result.exit_code == 1
        assert "not found" in result.stdout
