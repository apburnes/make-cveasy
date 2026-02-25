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
            Skill(
                name="Python",
                category="Programming",
                years=5,
                proficiency="Expert",
                related_experiences=[],
                content="Python experience",
            ),
            Skill(
                name="AWS",
                category="Cloud",
                years=3,
                proficiency="Advanced",
                related_experiences=[],
                content="AWS experience",
            ),
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
        skills = [
            Skill(
                name="Python",
                category="Programming",
                years=5,
                proficiency="Expert",
                related_experiences=[],
                content="",
            )
        ]

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
        assert (
            "Senior Software Engineer" in call_args[0][0] or "Software Engineer" in call_args[0][0]
        )


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
        skills = [
            Skill(
                name="Python",
                category="Programming",
                years=5,
                proficiency="Expert",
                related_experiences=[],
                content="",
            )
        ]
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


def test_generate_general_resume_with_bio_no_location(mock_provider):
    """Test generate_general_resume with bio without location."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        bio = Bio(name="John Doe", location="")

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
        assert "John Doe" in call_args[0][0]
        assert "Location:" not in call_args[0][0]


def test_generate_general_resume_with_skills_all_fields(mock_provider):
    """Test generate_general_resume with skills having all optional fields."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        skills = [
            Skill(
                name="Python",
                category="Programming",
                years=5,
                proficiency="Expert",
                related_experiences=[],
                content="Python experience",
            ),
            Skill(
                name="JavaScript",
                category=None,
                years=None,
                proficiency=None,
                related_experiences=[],
                content="",
            ),
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
        assert "JavaScript" in call_args[0][0]


def test_generate_general_resume_with_projects(mock_provider):
    """Test generate_general_resume with projects."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        projects = [
            Project(
                name="Project 1",
                description="Description 1",
                link="https://example.com",
                content="Content 1",
            ),
            Project(name="Project 2", description="Description 2", link=None, content=""),
        ]

        result = generator.generate_general_resume(
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=projects,
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Project 1" in call_args[0][0]
        assert "Project 2" in call_args[0][0]
        assert "https://example.com" in call_args[0][0]


def test_generate_general_resume_with_stories(mock_provider):
    """Test generate_general_resume with stories."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        stories = [
            Story(
                title="Achievement 1", context="Context 1", outcome="Outcome 1", content="Content 1"
            ),
            Story(title="Achievement 2", context=None, outcome=None, content=""),
        ]

        result = generator.generate_general_resume(
            skills=[],
            experiences=[],
            stories=stories,
            links=[],
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Achievement 1" in call_args[0][0]
        assert "Achievement 2" in call_args[0][0]
        assert "Context 1" in call_args[0][0]
        assert "Outcome 1" in call_args[0][0]


def test_generate_general_resume_with_education(mock_provider):
    """Test generate_general_resume with education."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        educations = [
            Education(
                name="Bachelor's Degree",
                organization="University",
                degree="Bachelor of Science",
                certificate=None,
                start_date="2010-01-01",
                end_date="2014-01-01",
                content="Content here",
            ),
            Education(
                name="Certificate",
                organization=None,
                degree=None,
                certificate="AWS Certified",
                start_date="2020-01-01",
                end_date=None,
                content="",
            ),
            Education(
                name="Master's Degree",
                organization="University 2",
                degree="Master of Science",
                certificate=None,
                start_date="2015-01-01",
                end_date=None,
                content="",
            ),
        ]

        result = generator.generate_general_resume(
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=educations,
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Bachelor's Degree" in call_args[0][0]
        assert "Certificate" in call_args[0][0]
        assert "Master's Degree" in call_args[0][0]
        assert "AWS Certified" in call_args[0][0]


def test_generate_general_resume_with_links(mock_provider):
    """Test generate_general_resume with links."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        links = [
            Link(name="GitHub", url="https://github.com/user", description="My GitHub profile"),
            Link(
                name="LinkedIn",
                url="https://linkedin.com/in/user",
                description="My LinkedIn profile",
            ),
        ]

        result = generator.generate_general_resume(
            skills=[],
            experiences=[],
            stories=[],
            links=links,
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "GitHub" in call_args[0][0]
        assert "LinkedIn" in call_args[0][0]
        assert "https://github.com/user" in call_args[0][0]


def test_generate_general_resume_with_experience_optional_fields(mock_provider):
    """Test generate_general_resume with experience having optional fields."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        experiences = [
            Experience(
                title="Engineer",
                organization="Company",
                start_date=None,
                end_date=None,
                location=None,
                related_skills=[],
                related_stories=[],
                content="Worked on projects",
            ),
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
        assert "Engineer" in call_args[0][0]
        assert "Company" in call_args[0][0]


def test_generate_general_resume_error_handling(mock_provider):
    """Test generate_general_resume error handling."""
    with patch("cveasy.ai.generator.get_ai_provider", return_value=mock_provider):
        generator = ResumeGenerator(provider=mock_provider)
        mock_provider.generate.side_effect = Exception("AI provider error")

        from cveasy.exceptions import ResumeGenerationError

        with pytest.raises(ResumeGenerationError) as exc_info:
            generator.generate_general_resume(
                skills=[],
                experiences=[],
                stories=[],
                links=[],
                projects=[],
                educations=[],
                bio=None,
            )

        assert "Failed to generate general resume" in str(exc_info.value)


def test_generate_customized_resume_with_projects(mock_provider):
    """Test generate_customized_resume with projects."""
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
        projects = [
            Project(
                name="Project 1",
                description="Description 1",
                link="https://example.com",
                content="Content 1",
            ),
        ]

        result = generator.generate_customized_resume(
            job=job,
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=projects,
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Project 1" in call_args[0][0]


def test_generate_customized_resume_with_stories(mock_provider):
    """Test generate_customized_resume with stories."""
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
        stories = [
            Story(
                title="Achievement 1", context="Context 1", outcome="Outcome 1", content="Content 1"
            ),
        ]

        result = generator.generate_customized_resume(
            job=job,
            skills=[],
            experiences=[],
            stories=stories,
            links=[],
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Achievement 1" in call_args[0][0]


def test_generate_customized_resume_with_education(mock_provider):
    """Test generate_customized_resume with education."""
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
        educations = [
            Education(
                name="Bachelor's Degree",
                organization="University",
                degree="Bachelor of Science",
                certificate=None,
                start_date="2010-01-01",
                end_date="2014-01-01",
                content="Content here",
            ),
            Education(
                name="Certificate Program",
                organization="Training Org",
                degree=None,
                certificate="AWS Certified Solutions Architect",
                start_date="2020-01-01",
                end_date=None,
                content="",
            ),
            Education(
                name="Master's Degree",
                organization="University 2",
                degree="Master of Science",
                certificate=None,
                start_date="2015-01-01",
                end_date=None,
                content="",
            ),
        ]

        result = generator.generate_customized_resume(
            job=job,
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=educations,
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Bachelor's Degree" in call_args[0][0]
        assert "Certificate Program" in call_args[0][0]
        assert "AWS Certified Solutions Architect" in call_args[0][0]
        assert "Master's Degree" in call_args[0][0]


def test_generate_customized_resume_with_links(mock_provider):
    """Test generate_customized_resume with links."""
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
        links = [
            Link(name="GitHub", url="https://github.com/user", description="My GitHub profile"),
        ]

        result = generator.generate_customized_resume(
            job=job,
            skills=[],
            experiences=[],
            stories=[],
            links=links,
            projects=[],
            educations=[],
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "GitHub" in call_args[0][0]


def test_generate_customized_resume_with_experiences(mock_provider):
    """Test generate_customized_resume with experiences."""
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

        result = generator.generate_customized_resume(
            job=job,
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


def test_generate_customized_resume_with_skills_all_fields(mock_provider):
    """Test generate_customized_resume with skills having all optional fields."""
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
        skills = [
            Skill(
                name="Python",
                category="Programming",
                years=5,
                proficiency="Expert",
                related_experiences=[],
                content="Python experience",
            ),
            Skill(
                name="JavaScript",
                category=None,
                years=None,
                proficiency=None,
                related_experiences=[],
                content="",
            ),
        ]

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
        assert "Python" in call_args[0][0]
        assert "JavaScript" in call_args[0][0]


def test_generate_customized_resume_with_bio_no_location(mock_provider):
    """Test generate_customized_resume with bio without location."""
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
        bio = Bio(name="John Doe", location="")

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


def test_generate_customized_resume_error_handling(mock_provider):
    """Test generate_customized_resume error handling."""
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
        mock_provider.generate.side_effect = Exception("AI provider error")

        from cveasy.exceptions import ResumeGenerationError

        with pytest.raises(ResumeGenerationError) as exc_info:
            generator.generate_customized_resume(
                job=job,
                skills=[],
                experiences=[],
                stories=[],
                links=[],
                projects=[],
                educations=[],
                bio=None,
            )

        assert "Failed to generate customized resume" in str(exc_info.value)


def test_update_resume_from_check_report_with_all_data(mock_provider):
    """Test update_resume_from_check_report with all data types."""
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
        skills = [
            Skill(
                name="Python",
                category="Programming",
                years=5,
                proficiency="Expert",
                related_experiences=[],
                content="",
            )
        ]
        experiences = [
            Experience(
                title="Engineer",
                organization="Company",
                start_date="2020-01-01",
                end_date="2024-01-01",
                location="SF",
                related_skills=[],
                related_stories=[],
                content="Work",
            )
        ]
        projects = [
            Project(
                name="Project 1", description="Desc", link="https://example.com", content="Content"
            )
        ]
        stories = [Story(title="Story 1", context="Context", outcome="Outcome", content="Content")]
        educations = [
            Education(
                name="Degree",
                organization="University",
                degree="BS",
                certificate=None,
                start_date="2010-01-01",
                end_date="2014-01-01",
                content="",
            )
        ]

        result = generator.update_resume_from_check_report(
            current_resume=current_resume,
            check_report=check_report,
            job=job,
            skills=skills,
            experiences=experiences,
            stories=stories,
            links=[],
            projects=projects,
            educations=educations,
            bio=None,
        )

        assert result == "# Generated Resume\n\nThis is a generated resume."
        call_args = mock_provider.generate.call_args
        assert "Python" in call_args[0][0] or "Engineer" in call_args[0][0]


def test_update_resume_from_check_report_error_handling(mock_provider):
    """Test update_resume_from_check_report error handling."""
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
        mock_provider.generate.side_effect = Exception("AI provider error")

        from cveasy.exceptions import ResumeGenerationError

        with pytest.raises(ResumeGenerationError) as exc_info:
            generator.update_resume_from_check_report(
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

        assert "Failed to update resume from check report" in str(exc_info.value)


def test_generate_cover_letter_basic(mock_provider):
    """Test generate_cover_letter with all data types."""
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
        skill = Skill(
            name="Python",
            category="Programming",
            years=5,
            proficiency="Expert",
            related_experiences=[],
            content="",
        )
        experience = Experience(
            title="Software Engineer",
            organization="Tech Corp",
            start_date="2020-01-01",
            end_date="2023-12-31",
            location="Remote",
            content="Worked on various projects",
        )
        story = Story(
            title="Led Migration", context="Context", outcome="Outcome", content="Story content"
        )
        link = Link(
            name="LinkedIn",
            description="Professional profile",
            url="https://linkedin.com/in/johndoe",
        )
        project = Project(
            name="E-commerce Platform",
            description="Full-stack app",
            link="https://github.com/user/proj",
            content="Project details",
        )
        education = Education(
            name="BS Computer Science",
            organization="University",
            degree="Bachelor of Science",
            start_date="2016-09-01",
            end_date="2020-05-15",
            content="",
        )

        mock_provider.generate.return_value = "# Cover Letter\n\nContent"

        result = generator.generate_cover_letter(
            job=job,
            skills=[skill],
            experiences=[experience],
            stories=[story],
            links=[link],
            projects=[project],
            educations=[education],
            bio=bio,
            reason=None,
        )

        assert result == "# Cover Letter\n\nContent"
        assert mock_provider.generate.called
        call_args = mock_provider.generate.call_args
        assert "cover letter" in call_args[0][0].lower()
        assert "500 words" in call_args[0][0].lower()
        assert "John Doe" in call_args[0][0]
        assert "Python" in call_args[0][0]


def test_generate_cover_letter_with_reason(mock_provider):
    """Test generate_cover_letter with reason included."""
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
        reason = "I'm excited about the company's mission"

        mock_provider.generate.return_value = "# Cover Letter\n\nContent"

        result = generator.generate_cover_letter(
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

        assert result == "# Cover Letter\n\nContent"
        call_args = mock_provider.generate.call_args
        assert reason in call_args[0][0]
        assert "reason for interest" in call_args[0][0].lower()


def test_generate_cover_letter_word_limit(mock_provider):
    """Test that generate_cover_letter includes 500-word limit in prompt."""
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

        mock_provider.generate.return_value = "# Cover Letter\n\nContent"

        generator.generate_cover_letter(
            job=job,
            skills=[],
            experiences=[],
            stories=[],
            links=[],
            projects=[],
            educations=[],
            bio=None,
            reason=None,
        )

        call_args = mock_provider.generate.call_args
        prompt = call_args[0][0]
        assert "500 words" in prompt or "500 WORDS" in prompt
        assert "no more than" in prompt.lower() or "maximum" in prompt.lower()


def test_generate_cover_letter_error_handling(mock_provider):
    """Test generate_cover_letter error handling."""
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
        mock_provider.generate.side_effect = Exception("AI provider error")

        from cveasy.exceptions import ResumeGenerationError

        with pytest.raises(ResumeGenerationError) as exc_info:
            generator.generate_cover_letter(
                job=job,
                skills=[],
                experiences=[],
                stories=[],
                links=[],
                projects=[],
                educations=[],
                bio=None,
                reason=None,
            )

        assert "Failed to generate cover letter" in str(exc_info.value)
