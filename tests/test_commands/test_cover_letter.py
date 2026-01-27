"""Tests for cover-letter command."""

from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cveasy.cli import app
from cveasy.models.job import Job
from cveasy.models.skill import Skill
from cveasy.models.bio import Bio


def test_generate_cover_letter_success(temp_dir, storage):
    """Test generating a cover letter successfully."""
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

    cover_letter_path = temp_dir / "applications" / application_id / "cover-letter.md"

    mock_service = MagicMock()
    mock_service.generate_cover_letter.return_value = cover_letter_path

    with patch("cveasy.commands.cover_letter.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.cover_letter.CoverLetterService", return_value=mock_service):
            result = runner.invoke(app, ["cover-letter", "--application", application_id])

            assert result.exit_code == 0
            assert f"Crafting personalized cover letter for application '{application_id}'" in result.stdout
            assert "Cover letter saved to" in result.stdout

            # Verify service was called with application_id
            mock_service.generate_cover_letter.assert_called_once_with(application_id, reason=None)


def test_generate_cover_letter_with_reason(temp_dir, storage):
    """Test generating a cover letter with reason flag."""
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

    cover_letter_path = temp_dir / "applications" / application_id / "cover-letter.md"

    mock_service = MagicMock()
    mock_service.generate_cover_letter.return_value = cover_letter_path

    reason = "I'm excited about the company's mission"

    with patch("cveasy.commands.cover_letter.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.cover_letter.CoverLetterService", return_value=mock_service):
            result = runner.invoke(app, ["cover-letter", "--application", application_id, "--reason", reason])

            assert result.exit_code == 0
            assert "Cover letter saved to" in result.stdout

            # Verify service was called with application_id and reason
            mock_service.generate_cover_letter.assert_called_once_with(application_id, reason=reason)


def test_generate_cover_letter_application_not_found(temp_dir, storage):
    """Test generating cover letter for non-existent application."""
    runner = CliRunner()

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.generate_cover_letter.side_effect = NotFoundError("Job application 'nonexistent-app' not found")

    with patch("cveasy.commands.cover_letter.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.cover_letter.CoverLetterService", return_value=mock_service):
            result = runner.invoke(app, ["cover-letter", "--application", "nonexistent-app"])

            assert result.exit_code == 1
            assert "not found" in result.stderr or "not found" in result.stdout


def test_generate_cover_letter_generation_error(temp_dir, storage):
    """Test generating cover letter when generation fails."""
    runner = CliRunner()

    from cveasy.exceptions import ResumeGenerationError

    mock_service = MagicMock()
    mock_service.generate_cover_letter.side_effect = ResumeGenerationError("AI generation failed")

    with patch("cveasy.commands.cover_letter.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.cover_letter.CoverLetterService", return_value=mock_service):
            result = runner.invoke(app, ["cover-letter", "--application", "test-app"])

            assert result.exit_code == 1
            assert "generation" in result.stderr.lower() or "generation" in result.stdout.lower()


def test_generate_cover_letter_token_usage(temp_dir, storage):
    """Test that token usage is displayed after generation."""
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

    cover_letter_path = temp_dir / "applications" / application_id / "cover-letter.md"

    mock_service = MagicMock()
    mock_service.generate_cover_letter.return_value = cover_letter_path

    with patch("cveasy.commands.cover_letter.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.cover_letter.CoverLetterService", return_value=mock_service):
            with patch("cveasy.commands.cover_letter.MeteredAIProvider.get_total_tokens", return_value=1000):
                with patch("cveasy.commands.cover_letter.MeteredAIProvider.get_input_tokens", return_value=600):
                    with patch("cveasy.commands.cover_letter.MeteredAIProvider.get_output_tokens", return_value=400):
                        result = runner.invoke(app, ["cover-letter", "--application", application_id])

                        assert result.exit_code == 0
                        assert "Token Usage" in result.stdout
                        assert "Input tokens" in result.stdout
                        assert "Output tokens" in result.stdout
                        assert "Total tokens" in result.stdout
