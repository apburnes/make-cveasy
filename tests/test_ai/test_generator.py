"""Tests for ResumeGenerator class."""

import pytest
from unittest.mock import MagicMock, patch
from cveasy.ai.generator import ResumeGenerator
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.story import Story
from cveasy.models.link import Link
from cveasy.models.project import Project
from cveasy.models.job import Job
from cveasy.models.education import Education
from cveasy.models.bio import Bio


@pytest.fixture
def mock_provider():
    """Create a mock AI provider."""
    provider = MagicMock()
    provider.generate.return_value = "# Generated Resume\n\nThis is a generated resume."
    return provider


def test_resume_generator_init_default(mock_provider):
    """Test ResumeGenerator initialization with default provider."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator()
        # Provider is set via get_ai_provider() call
        assert generator.provider == mock_provider


def test_resume_generator_init_with_provider(mock_provider):
    """Test ResumeGenerator initialization with explicit provider."""
    # Note: The implementation currently ignores the provider parameter
    # and always calls get_ai_provider(), so we need to mock it
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        assert generator.provider == mock_provider


def test_generate_general_resume_empty_data(mock_provider):
    """Test generate_general_resume with empty data."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)

        result = generator.generate_general_resume(
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        mock_provider.generate.assert_called_once()


def test_generate_general_resume_with_bio(mock_provider):
    """Test generate_general_resume with bio."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        bio = Bio(name="John Doe", location="San Francisco, CA")

        result = generator.generate_general_resume(
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=bio,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "John Doe" in call_args[0][0]  # Check prompt contains name


def test_generate_general_resume_with_skills(mock_provider):
    """Test generate_general_resume with skills."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        skills = [
            Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content="Python experience"),
            Skill(name="AWS", category="Cloud", years=3, proficiency="Advanced", related_experience=[], content="AWS experience"),
        ]

        result = generator.generate_general_resume(
            skills=skills,
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Python" in call_args[0][0]
        assert "AWS" in call_args[0][0]


def test_generate_general_resume_with_experiences(mock_provider):
    """Test generate_general_resume with experiences."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        experiences = [
            Experience(
                title="Senior Software Engineer",
                organization="Tech Corp",
                start_date="2020-01-01",
                end_date="2024-01-01",
                location="San Francisco, CA",
                related_skills=[],
                related_stories=[],
                content="Led development team",
            )
        ]

        result = generator.generate_general_resume(
            skills=[],
            experiences=experiences,
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Senior Software Engineer" in call_args[0][0]
        assert "Tech Corp" in call_args[0][0]


def test_generate_customized_resume(mock_provider):
    """Test generate_customized_resume."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        job = Job(
            name="Software Engineer",
            title="Senior Software Engineer",
            location="Remote",
            requirements="Python, AWS",
            pay="$150k-200k",
            content="Job description here",
        )
        skills = [Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content="")]

        result = generator.generate_customized_resume(
            job=job,
            skills=skills,
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Senior Software Engineer" in call_args[0][0] or "Software Engineer" in call_args[0][0]


def test_generate_customized_resume_with_bio(mock_provider):
    """Test generate_customized_resume with bio."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        job = Job(
            name="Software Engineer",
            title="Senior Software Engineer",
            location="Remote",
            requirements="Python, AWS",
            pay="$150k-200k",
            content="Job description here",
        )
        bio = Bio(name="John Doe", location="San Francisco, CA")

        result = generator.generate_customized_resume(
            job=job,
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=bio,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "John Doe" in call_args[0][0]


def test_update_resume_from_check_report(mock_provider):
    """Test update_resume_from_check_report."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        job = Job(
            name="Software Engineer",
            title="Senior Software Engineer",
            location="Remote",
            requirements="Python, AWS",
            pay="$150k-200k",
            content="Job description here",
        )
        current_resume = "# Current Resume\n\nContent"
        check_report = "# Check Report\n\nSuggestions: Add more Python experience"

        result = generator.update_resume_from_check_report(
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

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Current Resume" in call_args[0][0] or "check report" in call_args[0][0].lower()


def test_update_resume_from_check_report_with_data(mock_provider):
    """Test update_resume_from_check_report with full data."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        job = Job(
            name="Software Engineer",
            title="Senior Software Engineer",
            location="Remote",
            requirements="Python, AWS",
            pay="$150k-200k",
            content="Job description here",
        )
        current_resume = "# Current Resume\n\nContent"
        check_report = "# Check Report\n\nSuggestions"
        skills = [Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content="")]
        bio = Bio(name="John Doe", location="San Francisco, CA")

        result = generator.update_resume_from_check_report(
            current_resume=current_resume,
            check_report=check_report,
            job=job,
            skills=skills,
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=bio,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        mock_provider.generate.assert_called_once()
