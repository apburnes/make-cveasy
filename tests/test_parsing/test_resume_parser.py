"""Tests for resume parser."""

import json
import sys
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cveasy.parsing.resume_parser import (
    extract_text_from_pdf,
    extract_text_from_docx,
    parse_resume_with_llm,
    create_models_from_parsed_data,
)
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.project import Project
from cveasy.models.story import Story
from cveasy.models.education import Education
from cveasy.models.link import Link
from cveasy.models.bio import Bio


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
    pdf_path = temp_dir / "nonexistent.pdf"

    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf(pdf_path)


def test_extract_text_from_pdf_import_error(temp_dir):
    """Test PDF extraction when pypdf is not installed."""
    pdf_path = temp_dir / "test.pdf"
    pdf_path.touch()

    def import_side_effect(name, *args, **kwargs):
        if name == "pypdf":
            raise ImportError("No module named 'pypdf'")
        return __import__(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=import_side_effect):
        with pytest.raises(ImportError, match="pypdf package is required"):
            extract_text_from_pdf(pdf_path)


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
    docx_path = temp_dir / "nonexistent.docx"

    with pytest.raises(FileNotFoundError):
        extract_text_from_docx(docx_path)


def test_extract_text_from_docx_import_error(temp_dir):
    """Test DOCX extraction when python-docx is not installed."""
    docx_path = temp_dir / "test.docx"
    docx_path.touch()

    def import_side_effect(name, *args, **kwargs):
        if name == "docx":
            raise ImportError("No module named 'docx'")
        return __import__(name, *args, **kwargs)

    with patch("builtins.__import__", side_effect=import_side_effect):
        with pytest.raises(ImportError, match="python-docx package is required"):
            extract_text_from_docx(docx_path)


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
            {"name": "Python", "category": "Programming Language", "years": 5, "proficiency": "Expert"}
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "location": "San Francisco, CA",
                "content": "Developed software"
            }
        ],
        "projects": [
            {
                "name": "Web App",
                "description": "A web application",
                "link": "https://example.com",
                "content": "Built with React"
            }
        ],
        "stories": [
            {
                "title": "Led Migration",
                "context": "Company needed to scale",
                "outcome": "Reduced deployment time",
                "content": "Detailed description"
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
    mock_provider = Mock()
    mock_provider.generate.return_value = "This is not JSON"

    with pytest.raises(ValueError, match="Failed to parse LLM response as JSON"):
        parse_resume_with_llm("Sample resume text", mock_provider)


def test_create_models_from_parsed_data_complete():
    """Test model creation from complete parsed data."""
    parsed_data = {
        "skills": [
            {"name": "Python", "category": "Programming Language", "years": 5, "proficiency": "Expert"}
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "location": "San Francisco, CA",
                "content": "Developed software"
            }
        ],
        "projects": [
            {
                "name": "Web App",
                "description": "A web application",
                "link": "https://example.com",
                "content": "Built with React"
            }
        ],
        "stories": [
            {
                "title": "Led Migration",
                "context": "Company needed to scale",
                "outcome": "Reduced deployment time",
                "content": "Detailed description"
            }
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

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
            {
                "title": "Engineer",
                "organization": "Corp"
            },  # Valid
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

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

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

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

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
                "organization": "Corp"
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

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

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
                "related_experience": ["Software Engineer"]
            },
            {
                "name": "AWS",
                "category": "Cloud Platform",
                "related_experience": ["Software Engineer", "Cloud Architect"]
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "start_date": "2020-01-01",
                "end_date": "2024-01-01",
                "related_skills": ["Python", "AWS"],
                "related_stories": ["Led Migration"]
            },
            {
                "title": "Cloud Architect",
                "organization": "Cloud Inc",
                "start_date": "2024-01-01",
                "end_date": "Present",
                "related_skills": ["AWS"],
                "related_stories": []
            }
        ],
        "projects": [],
        "stories": [
            {
                "title": "Led Migration",
                "context": "Company needed to scale",
                "outcome": "Reduced deployment time",
                "content": "Detailed description"
            }
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    # Check experience -> skills relationships
    software_engineer = next((e for e in experiences if e.title == "Software Engineer"), None)
    assert software_engineer is not None
    assert len(software_engineer.related_skills) == 2
    assert "python" in software_engineer.related_skills  # slugified
    assert "aws" in software_engineer.related_skills

    # Check experience -> stories relationships
    assert len(software_engineer.related_stories) == 1
    assert "led-migration" in software_engineer.related_stories  # slugified

    # Check skill -> experience relationships
    python_skill = next((s for s in skills if s.name == "Python"), None)
    assert python_skill is not None
    assert len(python_skill.related_experience) == 1
    assert "software-engineer" in python_skill.related_experience  # slugified

    aws_skill = next((s for s in skills if s.name == "AWS"), None)
    assert aws_skill is not None
    assert len(aws_skill.related_experience) == 2
    assert "software-engineer" in aws_skill.related_experience
    assert "cloud-architect" in aws_skill.related_experience


def test_create_models_from_parsed_data_relationships_case_insensitive():
    """Test relationship matching is case-insensitive."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experience": ["SOFTWARE ENGINEER"]  # Different case
            },
            {
                "name": "AWS",
                "related_experience": []
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",  # Different case
                "organization": "Tech Corp",
                "related_skills": ["python", "AWS"]  # Different cases
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    experience = experiences[0]
    assert len(experience.related_skills) == 2
    assert "python" in experience.related_skills
    assert "aws" in experience.related_skills

    skill = skills[0]
    assert len(skill.related_experience) == 1
    assert "software-engineer" in skill.related_experience


def test_create_models_from_parsed_data_relationships_missing_references():
    """Test that missing relationship references are skipped gracefully."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experience": ["Non-existent Experience"]  # Doesn't exist
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": ["Python", "Non-existent Skill"],  # One doesn't exist
                "related_stories": ["Non-existent Story"]  # Doesn't exist
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    # Should only have the valid relationship
    experience = experiences[0]
    assert len(experience.related_skills) == 1
    assert "python" in experience.related_skills
    assert len(experience.related_stories) == 0  # Invalid story reference skipped

    # Skill should have no relationships since the experience doesn't exist
    skill = skills[0]
    assert len(skill.related_experience) == 0


def test_create_models_from_parsed_data_relationships_empty_arrays():
    """Test that empty relationship arrays are handled correctly."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experience": []  # Empty array
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": [],  # Empty array
                "related_stories": []  # Empty array
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    experience = experiences[0]
    assert len(experience.related_skills) == 0
    assert len(experience.related_stories) == 0

    skill = skills[0]
    assert len(skill.related_experience) == 0


def test_create_models_from_parsed_data_relationships_no_duplicates():
    """Test that duplicate relationships are not added."""
    parsed_data = {
        "skills": [
            {
                "name": "Python",
                "related_experience": ["Software Engineer", "Software Engineer"]  # Duplicate
            }
        ],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": ["Python", "Python", "Python"],  # Duplicates
                "related_stories": []
            }
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    experience = experiences[0]
    assert len(experience.related_skills) == 1  # Should only have one
    assert "python" in experience.related_skills

    skill = skills[0]
    assert len(skill.related_experience) == 1  # Should only have one
    assert "software-engineer" in skill.related_experience


def test_create_models_from_parsed_data_relationships_multiple_stories():
    """Test experience can have multiple related stories."""
    parsed_data = {
        "skills": [],
        "experiences": [
            {
                "title": "Software Engineer",
                "organization": "Tech Corp",
                "related_skills": [],
                "related_stories": ["Story 1", "Story 2", "Story 3"]
            }
        ],
        "projects": [],
        "stories": [
            {"title": "Story 1"},
            {"title": "Story 2"},
            {"title": "Story 3"}
        ],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    experience = experiences[0]
    assert len(experience.related_stories) == 3
    assert "story-1" in experience.related_stories
    assert "story-2" in experience.related_stories
    assert "story-3" in experience.related_stories


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
                "content": "Focused on software engineering"
            },
            {
                "name": "Master of Science",
                "organization": "Another University",
                "degree": "Master of Science",
                "start_date": "2022-09-01",
                "end_date": "2024-05-15"
            }
        ],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

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
                "url": "https://linkedin.com/in/user"
            },
            {
                "name": "GitHub",
                "description": "Code repository",
                "url": "https://github.com/user"
            }
        ],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

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

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

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

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    assert len(educations) == 1
    assert educations[0].name == "Bachelor of Science"


def test_create_models_from_parsed_data_with_bio():
    """Test bio model creation from parsed data."""
    parsed_data = {
        "bio": {
            "name": "John Doe",
            "location": "San Francisco, CA"
        },
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    assert bio is not None
    assert isinstance(bio, Bio)
    assert bio.name == "John Doe"
    assert bio.location == "San Francisco, CA"


def test_create_models_from_parsed_data_with_bio_no_location():
    """Test bio model creation without location - defaults to empty string."""
    parsed_data = {
        "bio": {
            "name": "John Doe"
        },
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    assert bio is not None
    assert isinstance(bio, Bio)
    assert bio.name == "John Doe"
    assert bio.location == ""  # Location defaults to empty string


def test_create_models_from_parsed_data_with_bio_no_name():
    """Test bio model creation is skipped when name is missing."""
    parsed_data = {
        "bio": {
            "location": "San Francisco, CA"
        },
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    bio, skills, experiences, projects, stories, educations, links = create_models_from_parsed_data(parsed_data)

    assert bio is None  # Should be None when name is missing
