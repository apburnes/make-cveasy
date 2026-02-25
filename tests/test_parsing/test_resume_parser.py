"""Tests for resume parser."""

import json
import re
import pytest
from unittest.mock import Mock, patch, MagicMock

from cveasy.parsing.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    parse_resume_with_llm,
    create_models_from_parsed_data,
    _normalize_name,
    _extract_aliases,
    _build_name_lookup,
    _resolve_name,
)
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.project import Project
from cveasy.models.story import Story
from cveasy.models.education import Education
from cveasy.models.link import Link
from cveasy.models.bio import Bio


def _matches_slug_pattern(slug: str, base: str) -> bool:
    """Check if slug matches the pattern base-[a-f0-9]{6}."""
    pattern = rf"^{re.escape(base)}-[a-f0-9]{{6}}$"
    return bool(re.match(pattern, slug))


def test_extract_text_from_pdf_success(temp_dir):
    """Test successful PDF text extraction."""
    # Create a mock PDF file
    pdf_path = temp_dir / "test.pdf"

    # Patch pypdf.PdfReader before the function imports it
    with patch("pypdf.PdfReader") as mock_reader_class:
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample PDF text content"
        mock_reader.pages = [mock_page]
        mock_reader_class.return_value = mock_reader

        # Create empty file
        pdf_path.touch()

        text = extract_text_from_pdf(pdf_path)

        assert text == "Sample PDF text content"
        mock_reader_class.assert_called_once_with(str(pdf_path))


def test_extract_text_from_pdf_file_not_found(temp_dir):
    """Test PDF extraction with missing file."""
    from cveasy.exceptions import DataImportError

    pdf_path = temp_dir / "nonexistent.pdf"

    with pytest.raises(DataImportError, match="PDF file not found"):
        extract_text_from_pdf(pdf_path)


@pytest.mark.skip(reason="Cannot easily mock import errors when package is installed")
def test_extract_text_from_pdf_import_error(temp_dir):
    """Test PDF extraction when pypdf is not installed.

    Note: This test is skipped because it's difficult to mock import errors
    when the package is actually installed. The error handling is tested
    implicitly through other integration tests.
    """
    pass


def test_extract_text_from_docx_success(temp_dir):
    """Test successful DOCX text extraction."""
    docx_path = temp_dir / "test.docx"

    # Patch docx.Document before the function imports it
    with patch("docx.Document") as mock_doc_class:
        mock_doc = MagicMock()
        mock_para1 = MagicMock()
        mock_para1.text = "First paragraph"
        mock_para2 = MagicMock()
        mock_para2.text = "Second paragraph"
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_doc_class.return_value = mock_doc

        # Create empty file
        docx_path.touch()

        text = extract_text_from_docx(docx_path)

        assert "First paragraph" in text
        assert "Second paragraph" in text
        mock_doc_class.assert_called_once_with(str(docx_path))


def test_extract_text_from_docx_file_not_found(temp_dir):
    """Test DOCX extraction with missing file."""
    from cveasy.exceptions import DataImportError

    docx_path = temp_dir / "nonexistent.docx"

    with pytest.raises(DataImportError, match="DOCX file not found"):
        extract_text_from_docx(docx_path)


@pytest.mark.skip(reason="Cannot easily mock import errors when package is installed")
def test_extract_text_from_docx_import_error(temp_dir):
    """Test DOCX extraction when python-docx is not installed.

    Note: This test is skipped because it's difficult to mock import errors
    when the package is actually installed. The error handling is tested
    implicitly through other integration tests.
    """
    pass


def test_extract_text_from_docx_filters_empty_paragraphs(temp_dir):
    """Test DOCX extraction filters out empty paragraphs."""
    docx_path = temp_dir / "test.docx"

    # Patch docx.Document before the function imports it
    with patch("docx.Document") as mock_doc_class:
        mock_doc = MagicMock()
        mock_para1 = MagicMock()
        mock_para1.text = "Content"
        mock_para2 = MagicMock()
        mock_para2.text = ""  # Empty paragraph
        mock_para3 = MagicMock()
        mock_para3.text = "   "  # Whitespace only
        mock_para4 = MagicMock()
        mock_para4.text = "More content"
        mock_doc.paragraphs = [mock_para1, mock_para2, mock_para3, mock_para4]
        mock_doc_class.return_value = mock_doc

        docx_path.touch()

        text = extract_text_from_docx(docx_path)

        assert "Content" in text
        assert "More content" in text
        # Empty paragraphs should be filtered
        assert text.count("\n") == 1  # Only one newline between paragraphs


def test_parse_resume_with_llm_success():
    """Test successful LLM parsing."""
    mock_provider = Mock()
    parsed_json = {
        "skills": [
            {
                "name": "Python",
                "category": "Programming Language",
                "years": 5,
                "proficiency": "Expert",
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "location": "San Francisco, CA",
                "content": "Developed software",
            }
        ],
        "projects": [
            {
                "name": "Web App",
                "description": "A web application",
                "link": "https://example.com",
                "content": "Built with React",
            }
        ],
        "stories": [
            {
                "title": "Led Migration",
                "context": "Company needed to scale",
                "outcome": "Reduced deployment time",
                "content": "Detailed description",
            }
        ],
        "education": [],
        "links": [],
    }
    mock_provider.generate.return_value = json.dumps(parsed_json)

    result = parse_resume_with_llm("Sample resume text", mock_provider)

    # Bio will be added as None if missing
    expected = parsed_json.copy()
    expected["bio"] = None
    assert result == expected
    assert "skills" in result
    assert "experiences" in result
    assert "projects" in result
    assert "stories" in result
    assert "education" in result
    assert "bio" in result


def test_parse_resume_with_llm_strips_markdown_code_blocks():
    """Test LLM parsing strips markdown code blocks."""
    mock_provider = Mock()
    parsed_json = {"skills": [], "experiences": [], "projects": [], "stories": [], "education": []}
    # Simulate LLM returning JSON wrapped in markdown code block
    parsed_json["links"] = []
    mock_provider.generate.return_value = "```json\n" + json.dumps(parsed_json) + "\n```"

    result = parse_resume_with_llm("Sample resume text", mock_provider)

    # Bio will be added as None if missing
    expected = parsed_json.copy()
    expected["bio"] = None
    assert result == expected


def test_parse_resume_with_llm_handles_missing_keys():
    """Test LLM parsing handles missing keys in response."""
    mock_provider = Mock()
    # LLM returns incomplete JSON
    incomplete_json = {"skills": [{"name": "Python"}]}
    mock_provider.generate.return_value = json.dumps(incomplete_json)

    result = parse_resume_with_llm("Sample resume text", mock_provider)

    # Should initialize missing keys
    assert "skills" in result
    assert "experiences" in result
    assert "projects" in result
    assert "stories" in result
    assert "education" in result
    assert "links" in result
    assert result["experiences"] == []
    assert result["projects"] == []
    assert result["stories"] == []
    assert result["education"] == []
    assert result["links"] == []


def test_parse_resume_with_llm_invalid_json():
    """Test LLM parsing with invalid JSON response."""
    from cveasy.exceptions import DataImportError

    mock_provider = Mock()
    mock_provider.generate.return_value = "This is not JSON"

    with pytest.raises(DataImportError, match="Failed to parse LLM response as JSON"):
        parse_resume_with_llm("Sample resume text", mock_provider)


def test_create_models_from_parsed_data_complete():
    """Test model creation from complete parsed data."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "category": "Programming Language",
                "years": 5,
                "proficiency": "Expert",
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "location": "San Francisco, CA",
                "content": "Developed software",
            }
        ],
        "projects": [
            {
                "name": "Web App",
                "description": "A web application",
                "link": "https://example.com",
                "content": "Built with React",
            }
        ],
        "stories": [
            {
                "title": "Led Migration",
                "context": "Company needed to scale",
                "outcome": "Reduced deployment time",
                "content": "Detailed description",
            }
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert bio is None  # No bio in this test data

    assert len(skills) == 1
    assert isinstance(skills[0], Skill)
    assert skills[0].name == "Python"
    assert skills[0].category == "Programming Language"

    assert len(experiences) == 1
    assert isinstance(experiences[0], Experience)
    assert experiences[0].title == "Software Engineer"
    assert experiences[0].organization == "Tech Corp"

    assert len(projects) == 1
    assert isinstance(projects[0], Project)
    assert projects[0].name == "Web App"

    assert len(stories) == 1
    assert isinstance(stories[0], Story)
    assert stories[0].title == "Led Migration"

    assert len(educations) == 0
    assert len(links) == 0
    assert len(links) == 0


def test_create_models_from_parsed_data_filters_incomplete():
    """Test model creation filters out incomplete entries."""
    parsed_data = {
        "skills": [
            {"name": "Python"},  # Valid
            {"category": "Language"},  # Missing name, should be skipped
        ],
        "experiences": [
            {"title": "Engineer", "organization": "Corp"},  # Valid
            {
                "title": "Manager"
                # Missing organization, should be skipped
            },
        ],
        "projects": [
            {"name": "Project1"},  # Valid
            {"description": "Project2"},  # Missing name, should be skipped
        ],
        "stories": [
            {"title": "Story1"},  # Valid
            {"context": "Story2"},  # Missing title, should be skipped
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert len(skills) == 1
    assert len(experiences) == 1
    assert len(projects) == 1
    assert len(stories) == 1


def test_create_models_from_parsed_data_empty():
    """Test model creation with empty parsed data."""
    parsed_data = {
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert len(skills) == 0
    assert len(experiences) == 0
    assert len(projects) == 0
    assert len(stories) == 0
    assert len(educations) == 0
    assert len(links) == 0


def test_create_models_from_parsed_data_optional_fields():
    """Test model creation handles optional fields correctly."""
    parsed_data = {
        "skills": [
            {"name": "Python"}  # Only required field
        ],
        "experiences": [
            {
                "title": "Engineer",
                "organization": "Corp",
                # Optional fields missing
            }
        ],
        "projects": [
            {"name": "Project", "description": "Desc"}  # No link
        ],
        "stories": [
            {"title": "Story"}  # No context or outcome
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert skills[0].category is None
    assert skills[0].years is None
    assert experiences[0].start_date is None
    assert projects[0].link is None
    assert stories[0].context is None
    assert len(educations) == 0
    assert len(links) == 0


def test_create_models_from_parsed_data_with_relationships():
    """Test model creation establishes relationships correctly."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "category": "Programming Language",
                "related_experiences": ["Software Engineer"],
            },
            {
                "name": "AWS",
                "category": "Cloud Platform",
                "related_experiences": ["Software Engineer", "Cloud Architect"],
            },
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "start_date": "2020-01",
                "end_date": "2024-01",
                "related_skills": ["Python", "AWS"],
                "related_stories": ["Led Migration"],
            },
            {
                "title": "Cloud Architect",
                "organization": "Cloud Inc",
                "start_date": "2024-01",
                "end_date": "Present",
                "related_skills": ["AWS"],
                "related_stories": [],
            },
        ],
        "projects": [],
        "stories": [
            {
                "title": "Led Migration",
                "context": "Company needed to scale",
                "outcome": "Reduced deployment time",
                "content": "Detailed description",
            }
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    # Check experience -> skills relationships (now actual model slugs with hex suffix)
    software_engineer = next((e for e in experiences if e.title == "Software Engineer"), None)
    assert software_engineer is not None
    assert len(software_engineer.related_skills) == 2
    assert any(s.startswith("python-") for s in software_engineer.related_skills)
    assert any(s.startswith("aws-") for s in software_engineer.related_skills)

    # Check experience -> stories relationships
    assert len(software_engineer.related_stories) == 1
    assert any(s.startswith("led-migration-") for s in software_engineer.related_stories)

    # Check skill -> experience relationships
    python_skill = next((s for s in skills if s.name == "Python"), None)
    assert python_skill is not None
    assert len(python_skill.related_experiences) == 1
    assert any(s.startswith("software-engineer-") for s in python_skill.related_experiences)

    aws_skill = next((s for s in skills if s.name == "AWS"), None)
    assert aws_skill is not None
    assert len(aws_skill.related_experiences) == 2
    assert any(s.startswith("software-engineer-") for s in aws_skill.related_experiences)
    assert any(s.startswith("cloud-architect-") for s in aws_skill.related_experiences)

    # Check story -> experience reverse relationships
    led_migration = next((s for s in stories if s.title == "Led Migration"), None)
    assert led_migration is not None
    assert len(led_migration.related_experiences) == 1
    assert any(s.startswith("software-engineer-") for s in led_migration.related_experiences)


def test_create_models_from_parsed_data_relationships_case_insensitive():
    """Test relationship matching is case-insensitive."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experiences": ["SOFTWARE ENGINEER"],  # Different case
            },
            {"name": "AWS", "related_experiences": []},
        ],
        "experiences": [
            {
                "title": "Software Engineer",  # Different case
                "organization": "Tech Corp",
                "related_skills": ["python", "AWS"],  # Different cases
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    assert len(experience.related_skills) == 2
    assert any(s.startswith("python-") for s in experience.related_skills)
    assert any(s.startswith("aws-") for s in experience.related_skills)

    skill = skills[0]
    assert len(skill.related_experiences) == 1
    assert any(s.startswith("software-engineer-") for s in skill.related_experiences)


def test_create_models_from_parsed_data_relationships_missing_references():
    """Test that missing relationship references are skipped gracefully."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experiences": ["Non-existent Experience"],  # Doesn't exist
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": ["Python", "Non-existent Skill"],  # One doesn't exist
                "related_stories": ["Non-existent Story"],  # Doesn't exist
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    # Should only have the valid relationship
    experience = experiences[0]
    assert len(experience.related_skills) == 1
    assert any(s.startswith("python-") for s in experience.related_skills)
    assert len(experience.related_stories) == 0  # Invalid story reference skipped

    # Skill's LLM-provided related_experiences pointed to a non-existent experience (skipped),
    # but the reverse relationship from experience -> skill populates it
    skill = skills[0]
    assert len(skill.related_experiences) == 1
    assert any(s.startswith("software-engineer-") for s in skill.related_experiences)


def test_create_models_from_parsed_data_relationships_empty_arrays():
    """Test that empty relationship arrays are handled correctly."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experiences": [],  # Empty array
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": [],  # Empty array
                "related_stories": [],  # Empty array
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    assert len(experience.related_skills) == 0
    assert len(experience.related_stories) == 0

    skill = skills[0]
    assert len(skill.related_experiences) == 0


def test_create_models_from_parsed_data_relationships_no_duplicates():
    """Test that duplicate relationships are not added."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experiences": ["Software Engineer", "Software Engineer"],  # Duplicate
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": ["Python", "Python", "Python"],  # Duplicates
                "related_stories": [],
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    assert len(experience.related_skills) == 1  # Should only have one
    assert any(s.startswith("python-") for s in experience.related_skills)

    skill = skills[0]
    assert len(skill.related_experiences) == 1  # Should only have one
    assert any(s.startswith("software-engineer-") for s in skill.related_experiences)


def test_create_models_from_parsed_data_relationships_multiple_stories():
    """Test experience can have multiple related stories."""
    parsed_data = {
        "skills": [],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": [],
                "related_stories": ["Story 1", "Story 2", "Story 3"],
            }
        ],
        "projects": [],
        "stories": [{"title": "Story 1"}, {"title": "Story 2"}, {"title": "Story 3"}],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    assert len(experience.related_stories) == 3
    assert any(s.startswith("story-1-") for s in experience.related_stories)
    assert any(s.startswith("story-2-") for s in experience.related_stories)
    assert any(s.startswith("story-3-") for s in experience.related_stories)

    # Check reverse relationships: stories should have related_experiences
    for story in stories:
        assert len(story.related_experiences) == 1
        assert any(s.startswith("software-engineer-") for s in story.related_experiences)


def test_create_models_from_parsed_data_with_education():
    """Test model creation includes education."""
    parsed_data = {
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [
            {
                "name": "Bachelor of Science in Computer Science",
                "organization": "University Name",
                "degree": "Bachelor of Science",
                "start_date": "2018-09-01",
                "end_date": "2022-05-15",
                "content": "Focused on software engineering",
            },
            {
                "name": "Master of Science",
                "organization": "Another University",
                "degree": "Master of Science",
                "start_date": "2022-09-01",
                "end_date": "2024-05-15",
            },
        ],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert len(educations) == 2
    assert isinstance(educations[0], Education)
    assert educations[0].name == "Bachelor of Science in Computer Science"
    assert educations[0].organization == "University Name"
    assert educations[0].degree == "Bachelor of Science"
    assert educations[1].name == "Master of Science"


def test_create_models_from_parsed_data_with_links():
    """Test model creation includes links."""
    parsed_data = {
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [
            {
                "name": "LinkedIn",
                "description": "Professional profile",
                "url": "https://linkedin.com/in/user",
            },
            {"name": "GitHub", "description": "Code repository", "url": "https://github.com/user"},
        ],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert len(links) == 2
    assert isinstance(links[0], Link)
    assert links[0].name == "LinkedIn"
    assert links[0].description == "Professional profile"
    assert links[0].url == "https://linkedin.com/in/user"
    assert links[1].name == "GitHub"
    assert links[1].url == "https://github.com/user"


def test_create_models_from_parsed_data_links_filters_incomplete():
    """Test link model creation filters out incomplete entries."""
    parsed_data = {
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [
            {"name": "LinkedIn", "url": "https://linkedin.com/in/user"},  # Valid
            {"name": "GitHub"},  # Missing url, should be skipped
            {"url": "https://example.com"},  # Missing name, should be skipped
        ],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert len(links) == 1
    assert links[0].name == "LinkedIn"
    assert links[0].url == "https://linkedin.com/in/user"


def test_create_models_from_parsed_data_education_filters_incomplete():
    """Test education model creation filters out incomplete entries."""
    parsed_data = {
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [
            {"name": "Bachelor of Science"},  # Valid
            {"organization": "University"},  # Missing name, should be skipped
        ],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert len(educations) == 1
    assert educations[0].name == "Bachelor of Science"


def test_create_models_from_parsed_data_with_bio():
    """Test bio model creation from parsed data."""
    parsed_data = {
        "bio": {"name": "John Doe", "location": "San Francisco, CA"},
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert bio is not None
    assert isinstance(bio, Bio)
    assert bio.name == "John Doe"
    assert bio.location == "San Francisco, CA"


def test_create_models_from_parsed_data_with_bio_no_location():
    """Test bio model creation without location - defaults to empty string."""
    parsed_data = {
        "bio": {"name": "John Doe"},
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert bio is not None
    assert isinstance(bio, Bio)
    assert bio.name == "John Doe"
    assert bio.location == ""  # Location defaults to empty string


def test_create_models_from_parsed_data_with_bio_no_name():
    """Test bio model creation is skipped when name is missing."""
    parsed_data = {
        "bio": {"location": "San Francisco, CA"},
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    assert bio is None  # Should be None when name is missing


def test_create_models_from_parsed_data_story_related_experiences():
    """Test story related_experiences from parsed data."""
    parsed_data = {
        "skills": [],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
            }
        ],
        "projects": [],
        "stories": [
            {
                "title": "Led Migration",
                "related_experiences": ["Software Engineer"],
            }
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    story = stories[0]
    assert len(story.related_experiences) == 1
    assert any(s.startswith("software-engineer-") for s in story.related_experiences)


def test_create_models_from_parsed_data_project_related_experiences():
    """Test project related_experiences from parsed data."""
    parsed_data = {
        "skills": [],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
            }
        ],
        "projects": [
            {
                "name": "Web App",
                "description": "A web application",
                "related_experiences": ["Software Engineer"],
            }
        ],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    project = projects[0]
    assert len(project.related_experiences) == 1
    assert any(s.startswith("software-engineer-") for s in project.related_experiences)


# ---------------------------------------------------------------------------
# Unit tests for _normalize_name
# ---------------------------------------------------------------------------


def test_normalize_name_lowercase():
    """Test normalization lowercases input."""
    assert _normalize_name("Python") == "python"
    assert _normalize_name("AWS") == "aws"


def test_normalize_name_parentheses():
    """Test normalization removes parens but keeps content."""
    assert _normalize_name("Amazon Web Services (AWS)") == "amazon web services aws"


def test_normalize_name_dots():
    """Test normalization removes dots."""
    assert _normalize_name("Node.js") == "nodejs"


def test_normalize_name_slashes():
    """Test normalization removes slashes."""
    assert _normalize_name("CI/CD") == "cicd"


def test_normalize_name_preserves_plus_hash():
    """Test normalization preserves + and #."""
    assert _normalize_name("C++") == "c++"
    assert _normalize_name("C#") == "c#"


def test_normalize_name_whitespace():
    """Test normalization collapses whitespace."""
    assert _normalize_name("  Machine   Learning  ") == "machine learning"


# ---------------------------------------------------------------------------
# Unit tests for _extract_aliases
# ---------------------------------------------------------------------------


def test_extract_aliases_parenthetical():
    """Test extracting aliases from parenthetical content."""
    aliases = _extract_aliases("Amazon Web Services (AWS)")
    assert "aws" in aliases
    assert "amazon web services" in aliases


def test_extract_aliases_acronym():
    """Test extracting acronym from 3+ word names."""
    aliases = _extract_aliases("Amazon Web Services")
    assert "aws" in aliases


def test_extract_aliases_simple_name():
    """Test simple single-word names return empty list."""
    aliases = _extract_aliases("Python")
    assert aliases == []


def test_extract_aliases_two_word_no_acronym():
    """Test two-word names don't generate acronym."""
    aliases = _extract_aliases("Machine Learning")
    # Two words = no acronym (requires 3+)
    assert not any(a == "ml" for a in aliases)


# ---------------------------------------------------------------------------
# Unit tests for _resolve_name
# ---------------------------------------------------------------------------


def test_resolve_name_exact():
    """Test resolution via exact match."""
    skill = Skill(name="Python", content="")
    lookup = _build_name_lookup([skill], "name")
    result = _resolve_name("Python", lookup)
    assert result is skill


def test_resolve_name_case_insensitive():
    """Test resolution via case-insensitive match."""
    skill = Skill(name="Python", content="")
    lookup = _build_name_lookup([skill], "name")
    result = _resolve_name("python", lookup)
    assert result is skill


def test_resolve_name_normalized():
    """Test resolution via normalized match."""
    skill = Skill(name="Node.js", content="")
    lookup = _build_name_lookup([skill], "name")
    result = _resolve_name("NodeJS", lookup)
    assert result is skill


def test_resolve_name_alias():
    """Test resolution via alias match."""
    skill = Skill(name="Amazon Web Services (AWS)", content="")
    lookup = _build_name_lookup([skill], "name")
    result = _resolve_name("AWS", lookup)
    assert result is skill


def test_resolve_name_no_match():
    """Test resolution returns None when nothing matches."""
    skill = Skill(name="Python", content="")
    lookup = _build_name_lookup([skill], "name")
    result = _resolve_name("Completely Different", lookup)
    assert result is None


# ---------------------------------------------------------------------------
# Integration tests for improved matching in create_models_from_parsed_data
# ---------------------------------------------------------------------------


def test_create_models_relationships_parenthetical_alias():
    """Test 'AWS' matches 'Amazon Web Services (AWS)' via alias."""
    parsed_data = {
        "skills": [
            {"name": "Amazon Web Services (AWS)", "category": "Cloud"},
        ],
        "experiences": [
            {
                "title": "Cloud Engineer",
                "organization": "Corp",
                "related_skills": ["AWS"],
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    assert len(experience.related_skills) == 1
    assert experience.related_skills[0] == skills[0].slug

    # Reverse relationship
    assert len(skills[0].related_experiences) == 1
    assert skills[0].related_experiences[0] == experience.slug


def test_create_models_relationships_punctuation_normalization():
    """Test 'NodeJS' matches 'Node.js' via normalization."""
    parsed_data = {
        "skills": [
            {"name": "Node.js", "category": "Runtime"},
        ],
        "experiences": [
            {
                "title": "Backend Dev",
                "organization": "Corp",
                "related_skills": ["NodeJS"],
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    assert len(experience.related_skills) == 1
    assert experience.related_skills[0] == skills[0].slug


def test_create_models_relationships_content_fallback():
    """Test skill mentioned in content but not in related_skills gets linked."""
    parsed_data = {
        "skills": [
            {"name": "Python", "category": "Language"},
            {"name": "Docker", "category": "Tool"},
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Corp",
                "related_skills": [],  # LLM didn't provide any
                "content": "Built microservices with Python and deployed using Docker containers.",
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    python_skill = next(s for s in skills if s.name == "Python")
    docker_skill = next(s for s in skills if s.name == "Docker")

    assert python_skill.slug in experience.related_skills
    assert docker_skill.slug in experience.related_skills


def test_create_models_relationships_content_scan_bidirectional():
    """Test content scan sets reverse relationships correctly."""
    parsed_data = {
        "skills": [
            {"name": "Kubernetes", "category": "Tool"},
        ],
        "experiences": [
            {
                "title": "DevOps Engineer",
                "organization": "Corp",
                "related_skills": [],
                "content": "Managed Kubernetes clusters for production workloads.",
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    skill = skills[0]

    # Forward: experience -> skill
    assert skill.slug in experience.related_skills
    # Reverse: skill -> experience
    assert experience.slug in skill.related_experiences


def test_create_models_relationships_content_scan_no_duplicates():
    """Test content scan doesn't duplicate existing LLM-matched relationships."""
    parsed_data = {
        "skills": [
            {"name": "Python", "category": "Language"},
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Corp",
                "related_skills": ["Python"],  # LLM already matched
                "content": "Developed services in Python.",  # Also in content
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    experience = experiences[0]
    python_skill = skills[0]

    # Should appear exactly once
    assert experience.related_skills.count(python_skill.slug) == 1
    assert python_skill.related_experiences.count(experience.slug) == 1


def test_create_models_relationships_content_short_names():
    """Test short name handling: 'C' in prose vs technical context."""
    parsed_data = {
        "skills": [
            {"name": "C", "category": "Language"},
            {"name": "Python", "category": "Language"},
        ],
        "experiences": [
            {
                "title": "Systems Programmer",
                "organization": "Corp",
                "related_skills": [],
                "content": "Wrote high-performance C code for embedded systems.",
            },
            {
                "title": "Manager",
                "organization": "Corp",
                "related_skills": [],
                "content": "I could not believe what a great team we had.",
            },
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(
        parsed_data
    )

    c_skill = next(s for s in skills if s.name == "C")
    systems_exp = next(e for e in experiences if e.title == "Systems Programmer")
    manager_exp = next(e for e in experiences if e.title == "Manager")

    # "C" should match in technical context (standalone C word)
    assert c_skill.slug in systems_exp.related_skills
    # "could" contains 'C' but pattern requires non-letter boundaries
    # and the word "could" won't match (?<![a-zA-Z])C(?![a-zA-Z+#])
    assert c_skill.slug not in manager_exp.related_skills
