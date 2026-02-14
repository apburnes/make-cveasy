"""Tests for ResumeService class."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from cveasy.services.resume_service import ResumeService
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
    generator.generate_general_resume.return_value = "# Generated Resume\n\nContent"
    generator.generate_customized_resume.return_value = "# Customized Resume\n\nContent"
    generator.update_resume_from_check_report.return_value = "# Updated Resume\n\nContent"
    return generator


@pytest.fixture
def resume_service(temp_dir, mock_storage, mock_generator):
    """Create a ResumeService instance with mocked dependencies."""
    with patch("cveasy.services.resume_service.MarkdownStorage", return_value=mock_storage):
        with patch("cveasy.services.resume_service.ResumeGenerator", return_value=mock_generator):
            service = ResumeService(temp_dir)
            service.storage = mock_storage
            service.generator = mock_generator
            return service


def test_resume_service_init(temp_dir):
    """Test ResumeService initialization."""
    with patch("cveasy.services.resume_service.MarkdownStorage") as mock_storage_class:
        with patch("cveasy.services.resume_service.ResumeGenerator") as mock_generator_class:
            ResumeService(temp_dir)

            mock_storage_class.assert_called_once_with(temp_dir)
            mock_generator_class.assert_called_once()


def test_generate_general_resume_success(resume_service, mock_storage, mock_generator):
    """Test successful general resume generation."""
    bio = Bio(name="John Doe", location="San Francisco, CA")
    skills = [
        Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experiences=[], content="")
    ]
    mock_storage.load_all_candidate_data.return_value = {
        "bio": bio,
        "skills": skills,
        "experiences": [],
        "stories": [],
        "links": [],
        "projects": [],
        "educations": [],
    }
    mock_storage.save_resume.return_value = Path("/tmp/resume.md")

    result = resume_service.generate_general_resume()

    assert result == Path("/tmp/resume.md")
    mock_storage.load_all_candidate_data.assert_called_once()
    mock_generator.generate_general_resume.assert_called_once()
    mock_storage.save_resume.assert_called_once_with("# Generated Resume\n\nContent")


def test_generate_general_resume_with_empty_data(resume_service, mock_storage, mock_generator):
    """Test general resume generation with empty data."""
    mock_storage.load_all_candidate_data.return_value = {
        "bio": None,
        "skills": [],
        "experiences": [],
        "stories": [],
        "links": [],
        "projects": [],
        "educations": [],
    }
    mock_storage.save_resume.return_value = Path("/tmp/resume.md")

    result = resume_service.generate_general_resume()

    assert result == Path("/tmp/resume.md")
    mock_generator.generate_general_resume.assert_called_once_with(
        skills=[],
        experiences=[],
        stories=[],
        links=[],
        projects=[],
        educations=[],
        bio=None,
    )


def test_generate_general_resume_storage_error(resume_service, mock_storage, mock_generator):
    """Test general resume generation when storage fails."""
    mock_storage.load_all_candidate_data.side_effect = Exception("Storage error")

    with pytest.raises(ResumeGenerationError) as exc_info:
        resume_service.generate_general_resume()

    assert "Failed to generate general resume" in str(exc_info.value)
    assert "Storage error" in str(exc_info.value)


def test_generate_general_resume_generator_error(resume_service, mock_storage, mock_generator):
    """Test general resume generation when generator fails."""
    mock_storage.load_all_candidate_data.return_value = {
        "bio": None, "skills": [], "experiences": [], "stories": [],
        "links": [], "projects": [], "educations": [],
    }
    mock_generator.generate_general_resume.side_effect = Exception("Generator error")

    with pytest.raises(ResumeGenerationError) as exc_info:
        resume_service.generate_general_resume()

    assert "Failed to generate general resume" in str(exc_info.value)
    assert "Generator error" in str(exc_info.value)


def test_generate_customized_resume_success(resume_service, mock_storage, mock_generator):
    """Test successful customized resume generation."""
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
    mock_storage.load_job.return_value = job
    mock_storage.load_all_candidate_data.return_value = {
        "bio": bio, "skills": [], "experiences": [], "stories": [],
        "links": [], "projects": [], "educations": [],
    }
    mock_storage.save_resume.return_value = Path("/tmp/custom-resume.md")

    result = resume_service.generate_customized_resume(application_id)

    assert result == Path("/tmp/custom-resume.md")
    mock_storage.load_job.assert_called_once_with(application_id)
    assert mock_generator.generate_customized_resume.call_count == 1
    call_args = mock_generator.generate_customized_resume.call_args
    assert call_args.kwargs["job"] == job
    assert call_args.kwargs["skills"] == []
    assert call_args.kwargs["bio"].name == "John Doe"
    assert call_args.kwargs["bio"].location == "San Francisco, CA"
    mock_storage.save_resume.assert_called_once_with(
        "# Customized Resume\n\nContent",
        application_id=application_id
    )


def test_generate_customized_resume_job_not_found(resume_service, mock_storage):
    """Test customized resume generation when job not found."""
    application_id = "nonexistent-app"
    mock_storage.load_job.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        resume_service.generate_customized_resume(application_id)

    assert f"Job application '{application_id}' not found" in str(exc_info.value)
    mock_storage.load_job.assert_called_once_with(application_id)


def test_generate_customized_resume_generation_error(resume_service, mock_storage, mock_generator):
    """Test customized resume generation when generation fails."""
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
    mock_storage.load_all_candidate_data.return_value = {
        "bio": None, "skills": [], "experiences": [], "stories": [],
        "links": [], "projects": [], "educations": [],
    }
    mock_generator.generate_customized_resume.side_effect = Exception("Generation failed")

    with pytest.raises(ResumeGenerationError) as exc_info:
        resume_service.generate_customized_resume(application_id)

    assert f"Failed to generate customized resume for application '{application_id}'" in str(exc_info.value)
    assert "Generation failed" in str(exc_info.value)


def test_update_resume_from_check_report_success(resume_service, mock_storage, mock_generator):
    """Test successful resume update from check report."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )
    current_resume = "# Current Resume\n\nContent"
    check_report = "# Check Report\n\nSuggestions here"

    mock_storage.load_job.return_value = job
    mock_storage.load_resume.return_value = current_resume
    mock_storage.load_check_report.return_value = check_report
    mock_storage.load_all_candidate_data.return_value = {
        "bio": None, "skills": [], "experiences": [], "stories": [],
        "links": [], "projects": [], "educations": [],
    }
    mock_storage.save_resume.return_value = Path("/tmp/updated-resume.md")

    result = resume_service.update_resume_from_check_report(application_id)

    assert result == Path("/tmp/updated-resume.md")
    mock_storage.load_job.assert_called_once_with(application_id)
    mock_storage.load_resume.assert_called_once_with(application_id=application_id)
    mock_storage.load_check_report.assert_called_once_with(application_id)
    mock_generator.update_resume_from_check_report.assert_called_once_with(
        current_resume=current_resume,
        check_report=check_report,
        job=job,
        skills=[],
        experiences=[],
        stories=[],
        links=[],
        projects=[],
        educations=[],
        bio=None,
    )
    mock_storage.save_resume.assert_called_once_with(
        "# Updated Resume\n\nContent",
        application_id=application_id
    )


def test_update_resume_from_check_report_job_not_found(resume_service, mock_storage):
    """Test resume update when job not found."""
    application_id = "nonexistent-app"
    mock_storage.load_job.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        resume_service.update_resume_from_check_report(application_id)

    assert f"Job application '{application_id}' not found" in str(exc_info.value)
    mock_storage.load_job.assert_called_once_with(application_id)
    mock_storage.load_resume.assert_not_called()


def test_update_resume_from_check_report_resume_not_found(resume_service, mock_storage):
    """Test resume update when resume not found."""
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
    mock_storage.load_resume.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        resume_service.update_resume_from_check_report(application_id)

    assert f"No resume found for application '{application_id}'" in str(exc_info.value)
    mock_storage.load_job.assert_called_once_with(application_id)
    mock_storage.load_resume.assert_called_once_with(application_id=application_id)
    mock_storage.load_check_report.assert_not_called()


def test_update_resume_from_check_report_check_report_not_found(resume_service, mock_storage):
    """Test resume update when check report not found."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )
    current_resume = "# Current Resume\n\nContent"

    mock_storage.load_job.return_value = job
    mock_storage.load_resume.return_value = current_resume
    mock_storage.load_check_report.return_value = None

    with pytest.raises(NotFoundError) as exc_info:
        resume_service.update_resume_from_check_report(application_id)

    assert f"No check report found for application '{application_id}'" in str(exc_info.value)
    mock_storage.load_job.assert_called_once_with(application_id)
    mock_storage.load_resume.assert_called_once_with(application_id=application_id)
    mock_storage.load_check_report.assert_called_once_with(application_id)


def test_update_resume_from_check_report_generation_error(resume_service, mock_storage, mock_generator):
    """Test resume update when generation fails."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )
    current_resume = "# Current Resume\n\nContent"
    check_report = "# Check Report\n\nSuggestions"

    mock_storage.load_job.return_value = job
    mock_storage.load_resume.return_value = current_resume
    mock_storage.load_check_report.return_value = check_report
    mock_storage.load_all_candidate_data.return_value = {
        "bio": None, "skills": [], "experiences": [], "stories": [],
        "links": [], "projects": [], "educations": [],
    }
    mock_generator.update_resume_from_check_report.side_effect = Exception("Update failed")

    with pytest.raises(ResumeGenerationError) as exc_info:
        resume_service.update_resume_from_check_report(application_id)

    assert f"Failed to update resume for application '{application_id}'" in str(exc_info.value)
    assert "Update failed" in str(exc_info.value)


def test_update_resume_from_check_report_preserves_not_found_error(resume_service, mock_storage):
    """Test that NotFoundError is preserved and not wrapped."""
    application_id = "test-app-20240101"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )
    current_resume = "# Current Resume\n\nContent"
    check_report = "# Check Report\n\nSuggestions"

    mock_storage.load_job.return_value = job
    mock_storage.load_resume.return_value = current_resume
    mock_storage.load_check_report.return_value = check_report
    mock_storage.load_all_candidate_data.side_effect = NotFoundError("Bio not found")

    with pytest.raises(NotFoundError) as exc_info:
        resume_service.update_resume_from_check_report(application_id)

    assert "Bio not found" in str(exc_info.value)


def test_get_resume_with_application_id(resume_service, mock_storage):
    """Test getting resume with application ID."""
    application_id = "test-app-20240101"
    resume_content = "# Resume\n\nContent"
    mock_storage.load_resume.return_value = resume_content

    result = resume_service.get_resume(application_id=application_id)

    assert result == resume_content
    mock_storage.load_resume.assert_called_once_with(application_id=application_id, date=None)


def test_get_resume_with_date(resume_service, mock_storage):
    """Test getting resume with date."""
    date = "20240101"
    resume_content = "# Resume\n\nContent"
    mock_storage.load_resume.return_value = resume_content

    result = resume_service.get_resume(date=date)

    assert result == resume_content
    mock_storage.load_resume.assert_called_once_with(application_id=None, date=date)


def test_get_resume_not_found(resume_service, mock_storage):
    """Test getting resume when not found."""
    mock_storage.load_resume.return_value = None

    result = resume_service.get_resume()

    assert result is None
    mock_storage.load_resume.assert_called_once_with(application_id=None, date=None)


def test_get_resume_with_both_params(resume_service, mock_storage):
    """Test getting resume with both application_id and date."""
    application_id = "test-app-20240101"
    date = "20240101"
    resume_content = "# Resume\n\nContent"
    mock_storage.load_resume.return_value = resume_content

    result = resume_service.get_resume(application_id=application_id, date=date)

    assert result == resume_content
    mock_storage.load_resume.assert_called_once_with(application_id=application_id, date=date)
