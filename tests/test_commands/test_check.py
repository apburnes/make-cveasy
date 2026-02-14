"""Tests for check command."""

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
    storage.save_resume("# Resume\n\nContent here with enough text to pass the minimum length validation check.", application_id=application_id)
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experiences=[], content=""))

    report_content = "# Check Report\n\nAnalysis here"
    report_path = temp_dir / "applications" / application_id / "check-report.md"

    mock_service = MagicMock()
    mock_service.check_resume.return_value = (report_content, report_path)

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.check.CheckService", return_value=mock_service):
            with patch("cveasy.ai.providers.get_ai_provider"):
                result = runner.invoke(app, ["check", "--application", application_id])

                assert result.exit_code == 0
                assert "Generating quality report with AI" in result.stdout
                assert "Check report saved to" in result.stdout

                # Verify service was called
                mock_service.check_resume.assert_called_once_with(application_id)


def test_check_application_not_found(temp_dir, storage):
    """Test check command when application doesn't exist."""
    runner = CliRunner()

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.check_resume.side_effect = NotFoundError("Job application 'nonexistent-app' not found")

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.check.CheckService", return_value=mock_service):
            with patch("cveasy.ai.providers.get_ai_provider"):
                result = runner.invoke(app, ["check", "--application", "nonexistent-app"])

                assert result.exit_code == 1
                assert "not found" in result.stderr or "not found" in result.stdout


def test_check_job_not_found(temp_dir, storage):
    """Test check command when job doesn't exist (edge case)."""
    runner = CliRunner()

    application_id = "test-app-20240101"
    # Create application directory but no job file
    (temp_dir / "applications" / application_id).mkdir(parents=True)

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.check_resume.side_effect = NotFoundError("Job application 'test-app-20240101' not found")

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.check.CheckService", return_value=mock_service):
            with patch("cveasy.ai.providers.get_ai_provider"):
                result = runner.invoke(app, ["check", "--application", application_id])

                assert result.exit_code == 1
                assert "not found" in result.stderr or "not found" in result.stdout


def test_check_without_application_prompts_and_uses_selection(temp_dir, storage):
    """Test check without --application prompts to select and uses selected application."""
    runner = CliRunner()
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
    storage.save_resume("# Resume\n\nContent here with enough text to pass the minimum length validation check.", application_id=application_id)
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experiences=[], content=""))

    report_content = "# Check Report\n\nAnalysis here"
    report_path = temp_dir / "applications" / application_id / "check-report.md"
    mock_service = MagicMock()
    mock_service.check_resume.return_value = (report_content, report_path)

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.check.CheckService", return_value=mock_service):
            with patch("cveasy.commands.check.prompt_select_application", return_value=application_id):
                with patch("cveasy.ai.providers.get_ai_provider"):
                    result = runner.invoke(app, ["check"])

    assert result.exit_code == 0
    assert "Generating quality report with AI" in result.stdout
    mock_service.check_resume.assert_called_once_with(application_id)


def test_check_with_select_flag_uses_selection(temp_dir, storage):
    """Test check with --select flag prompts and uses selected application."""
    runner = CliRunner()
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
    storage.save_resume("# Resume\n\nContent here with enough text to pass the minimum length validation check.", application_id=application_id)
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experiences=[], content=""))

    report_content = "# Check Report\n\nAnalysis here"
    report_path = temp_dir / "applications" / application_id / "check-report.md"
    mock_service = MagicMock()
    mock_service.check_resume.return_value = (report_content, report_path)

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.check.CheckService", return_value=mock_service):
            with patch("cveasy.commands.check.prompt_select_application", return_value=application_id):
                with patch("cveasy.ai.providers.get_ai_provider"):
                    result = runner.invoke(app, ["check", "--select"])

    assert result.exit_code == 0
    assert "Generating quality report with AI" in result.stdout
    mock_service.check_resume.assert_called_once_with(application_id)


def test_check_without_application_when_helper_returns_none_exits_one(temp_dir, storage):
    """Test check without --application when helper returns None exits with code 1."""
    runner = CliRunner()

    with patch("cveasy.commands.check.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.check.prompt_select_application", return_value=None):
            result = runner.invoke(app, ["check"])

    assert result.exit_code == 1
