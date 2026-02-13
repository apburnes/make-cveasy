"""Tests for generate command."""

from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cveasy.cli import app
from cveasy.cli_utils import GENERAL_RESUME_CHOICE
from cveasy.models.job import Job
from cveasy.models.skill import Skill
from cveasy.models.bio import Bio


def test_generate_general_resume(temp_dir, storage):
    """Test generating a general resume with --no-select."""
    runner = CliRunner()

    # Set up some data
    bio = Bio(name="John Doe", location="San Francisco, CA")
    storage.save_bio(bio)
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content=""))

    resume_path = temp_dir / "resume" / "resume-20240101.md"

    mock_service = MagicMock()
    mock_service.generate_general_resume.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            result = runner.invoke(app, ["generate", "--no-select"])

    assert result.exit_code == 0
    assert "Crafting your general resume with AI" in result.stdout
    assert "Resume saved to" in result.stdout
    mock_service.generate_general_resume.assert_called_once()


def test_generate_customized_resume(temp_dir, storage):
    """Test generating a customized resume for an application."""
    runner = CliRunner()

    # Set up application
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

    bio = Bio(name="John Doe", location="San Francisco, CA")
    storage.save_bio(bio)
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content=""))

    resume_path = temp_dir / "applications" / application_id / "resume.md"

    mock_service = MagicMock()
    mock_service.generate_customized_resume.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            result = runner.invoke(app, ["generate", "--application", application_id])

            assert result.exit_code == 0
            assert "Crafting your customized resume with AI" in result.stdout
            assert "Resume saved to" in result.stdout

            # Verify service was called with application_id
            mock_service.generate_customized_resume.assert_called_once_with(application_id)


def test_generate_customized_resume_application_not_found(temp_dir, storage):
    """Test generating resume for non-existent application."""
    runner = CliRunner()

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.generate_customized_resume.side_effect = NotFoundError("Job application 'nonexistent-app' not found")

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            result = runner.invoke(app, ["generate", "--application", "nonexistent-app"])

            assert result.exit_code == 1
            assert "not found" in result.stderr or "not found" in result.stdout


def test_generate_update_resume(temp_dir, storage):
    """Test updating resume from check report."""
    runner = CliRunner()

    # Set up application with resume and check report
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
    storage.save_resume("# Current Resume\n\nContent with enough text to pass the minimum length validation check.", application_id=application_id)
    storage.save_check_report("# Check Report\n\nSuggestions here with enough content to pass the minimum length validation.", application_id)

    bio = Bio(name="John Doe", location="San Francisco, CA")
    storage.save_bio(bio)

    resume_path = temp_dir / "applications" / application_id / "resume.md"

    mock_service = MagicMock()
    mock_service.update_resume_from_check_report.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            result = runner.invoke(app, ["generate", "--application", application_id, "--update"])

            assert result.exit_code == 0
            assert "Analyzing check report and updating resume" in result.stdout
            assert "Resume updated and saved to" in result.stdout

            # Verify service was called
            mock_service.update_resume_from_check_report.assert_called_once_with(application_id)


def test_generate_update_with_select_flow(temp_dir, storage):
    """Test generate --update with select flow (no --application) prompts then updates."""
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
    storage.save_resume("# Current Resume\n\nContent with enough text to pass the minimum length validation check.", application_id=application_id)
    storage.save_check_report("# Check Report\n\nSuggestions here with enough content to pass the minimum length validation.", application_id)
    storage.save_bio(Bio(name="John Doe", location="San Francisco, CA"))

    resume_path = temp_dir / "applications" / application_id / "resume.md"
    mock_service = MagicMock()
    mock_service.update_resume_from_check_report.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            with patch("cveasy.commands.generate.prompt_select_application", return_value=application_id):
                result = runner.invoke(app, ["generate", "--update"])

    assert result.exit_code == 0
    assert "Analyzing check report and updating resume" in result.stdout
    assert "Resume updated and saved to" in result.stdout
    mock_service.update_resume_from_check_report.assert_called_once_with(application_id)


def test_generate_update_resume_no_resume(temp_dir, storage):
    """Test updating resume when resume doesn't exist."""
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

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.update_resume_from_check_report.side_effect = NotFoundError("No resume found for application")

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            result = runner.invoke(app, ["generate", "--application", application_id, "--update"])

            assert result.exit_code == 1
            assert "No resume found" in result.stderr or "No resume found" in result.stdout


def test_generate_update_resume_no_check_report(temp_dir, storage):
    """Test updating resume when check report doesn't exist."""
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
    storage.save_resume("# Current Resume\n\nContent with enough text to pass the minimum length validation check.", application_id=application_id)

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.update_resume_from_check_report.side_effect = NotFoundError("No check report found for application")

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            result = runner.invoke(app, ["generate", "--application", application_id, "--update"])

            assert result.exit_code == 1
            assert "No check report found" in result.stderr or "No check report found" in result.stdout


def test_generate_with_select_uses_selected_application(temp_dir, storage):
    """Test generate (default) prompts and uses selected application."""
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
    from cveasy.models.bio import Bio
    from cveasy.models.skill import Skill

    storage.save_bio(Bio(name="John Doe", location="San Francisco, CA"))
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content=""))

    resume_path = temp_dir / "applications" / application_id / "resume.md"
    mock_service = MagicMock()
    mock_service.generate_customized_resume.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            with patch("cveasy.commands.generate.prompt_select_application", return_value=application_id):
                result = runner.invoke(app, ["generate"])

    assert result.exit_code == 0
    assert "Crafting your customized resume with AI" in result.stdout
    mock_service.generate_customized_resume.assert_called_once_with(application_id)


def test_generate_with_explicit_select_flag_uses_selection(temp_dir, storage):
    """Test generate with explicit --select flag prompts and uses selected application."""
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
    storage.save_bio(Bio(name="John Doe", location="San Francisco, CA"))
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content=""))

    resume_path = temp_dir / "applications" / application_id / "resume.md"
    mock_service = MagicMock()
    mock_service.generate_customized_resume.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            with patch("cveasy.commands.generate.prompt_select_application", return_value=application_id):
                result = runner.invoke(app, ["generate", "--select"])

    assert result.exit_code == 0
    assert "Crafting your customized resume with AI" in result.stdout
    mock_service.generate_customized_resume.assert_called_once_with(application_id)


def test_generate_with_select_general_resume_choice(temp_dir, storage):
    """Test generate when user selects general resume from picker calls generate_general_resume."""
    runner = CliRunner()
    storage.save_bio(Bio(name="John Doe", location="San Francisco, CA"))
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content=""))
    resume_path = temp_dir / "resume" / "resume-20240101.md"
    mock_service = MagicMock()
    mock_service.generate_general_resume.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            with patch(
                "cveasy.commands.generate.prompt_select_application",
                return_value=GENERAL_RESUME_CHOICE,
            ):
                result = runner.invoke(app, ["generate"])

    assert result.exit_code == 0
    assert "Crafting your general resume with AI" in result.stdout
    mock_service.generate_general_resume.assert_called_once()
    mock_service.generate_customized_resume.assert_not_called()


def test_generate_with_select_no_application_exits_one(temp_dir, storage):
    """Test generate (default) when helper returns None exits with code 1."""
    runner = CliRunner()

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.prompt_select_application", return_value=None):
            result = runner.invoke(app, ["generate"])

    assert result.exit_code == 1


def test_generate_with_application_ignores_select(temp_dir, storage):
    """Test that --application skips prompt and uses given application."""
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
    from cveasy.models.bio import Bio
    from cveasy.models.skill import Skill

    storage.save_bio(Bio(name="John Doe", location="San Francisco, CA"))
    storage.save_skill(Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content=""))

    resume_path = temp_dir / "applications" / application_id / "resume.md"
    mock_service = MagicMock()
    mock_service.generate_customized_resume.return_value = resume_path

    with patch("cveasy.commands.generate.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.generate.ResumeService", return_value=mock_service):
            with patch("cveasy.commands.generate.prompt_select_application") as mock_prompt:
                result = runner.invoke(app, ["generate", "--application", application_id])

    assert result.exit_code == 0
    mock_prompt.assert_not_called()
    mock_service.generate_customized_resume.assert_called_once_with(application_id)
