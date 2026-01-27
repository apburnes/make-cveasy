"""Tests for CoverLetterService class."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from cveasy.services.cover_letter_service import CoverLetterService
from cveasy.exceptions import NotFoundError, ResumeGenerationError
from cveasy.models.job import Job
from cveasy.models.bio import Bio
from cveasy.models.skill import Skill


@pytest.fixture
def mock_storage():
    """Create a mock MarkdownStorage."""
    storage = MagicMock()
    return storage


@pytest.fixture
def mock_generator():
    """Create a mock ResumeGenerator."""
    generator = MagicMock()
    generator.generate_cover_letter.return_value = "# Cover Letter\n\nContent"
    return generator


@pytest.fixture
def cover_letter_service(temp_dir, mock_storage, mock_generator):
    """Create a CoverLetterService instance with mocked dependencies."""
    with patch("cveasy.services.cover_letter_service.MarkdownStorage", return_value=mock_storage):
        with patch("cveasy.services.cover_letter_service.ResumeGenerator", return_value=mock_generator):
            service = CoverLetterService(temp_dir)
            service.storage = mock_storage
            service.generator = mock_generator
            return service


def test_cover_letter_service_init(temp_dir):
    """Test CoverLetterService initialization."""
    with patch("cveasy.services.cover_letter_service.MarkdownStorage") as mock_storage_class:
        with patch("cveasy.services.cover_letter_service.ResumeGenerator") as mock_generator_class:
            CoverLetterService(temp_dir)

            mock_storage_class.assert_called_once_with(temp_dir)
            mock_generator_class.assert_called_once()


def test_generate_cover_letter_success(cover_letter_service, mock_storage, mock_generator):
    """Test successful cover letter generation."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )
    bio = Bio(name="John Doe", location="San Francisco, CA")
    skill = Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content="")

    mock_storage.load_job.return_value = job
    mock_storage.load_bio.return_value = bio
    mock_storage.list_skills.return_value = [skill]
    mock_storage.list_experiences.return_value = []
    mock_storage.list_stories.return_value = []
    mock_storage.list_links.return_value = []
    mock_storage.list_projects.return_value = []
    mock_storage.list_educations.return_value = []

    expected_path = Path("applications") / application_id / "cover-letter.md"
    mock_storage.save_cover_letter.return_value = expected_path

    result = cover_letter_service.generate_cover_letter(application_id)

    assert result == expected_path
    mock_storage.load_job.assert_called_once_with(application_id)
    mock_generator.generate_cover_letter.assert_called_once_with(
        job=job,
        skills=[skill],
        experiences=[],
        stories=[],
        links=[],
        projects=[],
        educations=[],
        bio=bio,
        reason=None,
    )
    mock_storage.save_cover_letter.assert_called_once_with("# Cover Letter\n\nContent", application_id=application_id)


def test_generate_cover_letter_with_reason(cover_letter_service, mock_storage, mock_generator):
    """Test cover letter generation with reason parameter."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )

    mock_storage.load_job.return_value = job
    mock_storage.load_bio.return_value = None
    mock_storage.list_skills.return_value = []
    mock_storage.list_experiences.return_value = []
    mock_storage.list_stories.return_value = []
    mock_storage.list_links.return_value = []
    mock_storage.list_projects.return_value = []
    mock_storage.list_educations.return_value = []

    expected_path = Path("applications") / application_id / "cover-letter.md"
    mock_storage.save_cover_letter.return_value = expected_path

    reason = "I'm excited about the company's mission"
    result = cover_letter_service.generate_cover_letter(application_id, reason=reason)

    assert result == expected_path
    mock_generator.generate_cover_letter.assert_called_once_with(
        job=job,
        skills=[],
        experiences=[],
        stories=[],
        links=[],
        projects=[],
        educations=[],
        bio=None,
        reason=reason,
    )


def test_generate_cover_letter_job_not_found(cover_letter_service, mock_storage):
    """Test cover letter generation when job is not found."""
    application_id = "nonexistent-app"
    mock_storage.load_job.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        cover_letter_service.generate_cover_letter(application_id)

    assert f"Job application '{application_id}' not found" in str(exc_info.value)
    mock_storage.load_job.assert_called_once_with(application_id)


def test_generate_cover_letter_generation_error(cover_letter_service, mock_storage, mock_generator):
    """Test cover letter generation when generation fails."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )

    mock_storage.load_job.return_value = job
    mock_storage.load_bio.return_value = None
    mock_storage.list_skills.return_value = []
    mock_storage.list_experiences.return_value = []
    mock_storage.list_stories.return_value = []
    mock_storage.list_links.return_value = []
    mock_storage.list_projects.return_value = []
    mock_storage.list_educations.return_value = []
    mock_generator.generate_cover_letter.side_effect = Exception("Generation failed")

    with pytest.raises(ResumeGenerationError) as exc_info:
        cover_letter_service.generate_cover_letter(application_id)

    assert f"Failed to generate cover letter for application '{application_id}'" in str(exc_info.value)
    assert "Generation failed" in str(exc_info.value)
