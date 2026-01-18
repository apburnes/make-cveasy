"""Tests for ImportService class."""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from cveasy.services.import_service import ImportService
from cveasy.exceptions import ValidationError, ImportError
from cveasy.models.bio import Bio
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.story import Story
from cveasy.models.link import Link
from cveasy.models.project import Project
from cveasy.models.education import Education


@pytest.fixture
def mock_storage():
    """Create a mock MarkdownStorage."""
    storage = MagicMock()
    return storage


@pytest.fixture
def import_service(temp_dir, mock_storage):
    """Create an ImportService instance with mocked storage."""
    with patch("cveasy.services.import_service.MarkdownStorage", return_value=mock_storage):
        service = ImportService(temp_dir)
        service.storage = mock_storage
        return service


def test_import_service_init(temp_dir):
    """Test ImportService initialization."""
    with patch("cveasy.services.import_service.MarkdownStorage") as mock_storage_class:
        service = ImportService(temp_dir)

        mock_storage_class.assert_called_once_with(temp_dir)


def test_import_resume_pdf_success(import_service, mock_storage, temp_dir):
    """Test successful import from PDF file."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy pdf content")

    extracted_text = "John Doe\nSoftware Engineer\nPython, AWS"
    parsed_data = {
        "bio": {"name": "John Doe", "location": "San Francisco, CA"},
        "skills": [{"name": "Python", "category": "Programming"}],
        "experiences": [],
        "projects": [],
        "stories": [],
        "educations": [],
        "links": [],
    }

    bio = Bio(name="John Doe", location="San Francisco, CA")
    skill = Skill(name="Python", category="Programming", years=0, proficiency="", related_experience=[], content="")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (bio, [skill], [], [], [], [], [])
                    mock_storage.load_bio.return_value = None
                    mock_storage.load_skill.return_value = None

                    stats = import_service.import_resume(pdf_path)

                    assert stats["imported_bio"] == 1
                    assert stats["updated_bio"] == 0
                    assert stats["imported_skills"] == 1
                    assert stats["skipped_skills"] == 0
                    mock_storage.save_bio.assert_called_once()
                    mock_storage.save_skill.assert_called_once()


def test_import_resume_docx_success(import_service, mock_storage, temp_dir):
    """Test successful import from DOCX file."""
    docx_path = temp_dir / "resume.docx"
    docx_path.write_text("dummy docx content")

    extracted_text = "John Doe\nSoftware Engineer\nPython, AWS"
    parsed_data = {
        "bio": {"name": "John Doe", "location": "San Francisco, CA"},
        "skills": [{"name": "Python", "category": "Programming"}],
        "experiences": [],
        "projects": [],
        "stories": [],
        "educations": [],
        "links": [],
    }

    bio = Bio(name="John Doe", location="San Francisco, CA")
    skill = Skill(name="Python", category="Programming", years=0, proficiency="", related_experience=[], content="")

    with patch("cveasy.services.import_service.extract_text_from_docx", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (bio, [skill], [], [], [], [], [])
                    mock_storage.load_bio.return_value = None
                    mock_storage.load_skill.return_value = None

                    stats = import_service.import_resume(docx_path)

                    assert stats["imported_bio"] == 1
                    assert stats["imported_skills"] == 1
                    mock_storage.save_bio.assert_called_once()
                    mock_storage.save_skill.assert_called_once()


def test_import_resume_file_not_found(import_service, temp_dir):
    """Test import when file doesn't exist."""
    nonexistent_path = temp_dir / "nonexistent.pdf"

    with pytest.raises(ValidationError) as exc_info:
        import_service.import_resume(nonexistent_path)

    assert "File not found" in str(exc_info.value)
    assert str(nonexistent_path) in str(exc_info.value)


def test_import_resume_unsupported_file_type(import_service, temp_dir):
    """Test import with unsupported file type."""
    txt_path = temp_dir / "resume.txt"
    txt_path.write_text("dummy content")

    with pytest.raises(ValidationError) as exc_info:
        import_service.import_resume(txt_path)

    assert "Unsupported file type" in str(exc_info.value)
    assert ".txt" in str(exc_info.value) or "'.txt'" in str(exc_info.value)


def test_import_resume_text_extraction_error(import_service, temp_dir):
    """Test import when text extraction fails."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")

    with patch("cveasy.services.import_service.extract_text_from_pdf", side_effect=Exception("Extraction failed")):
        with pytest.raises(ImportError) as exc_info:
            import_service.import_resume(pdf_path)

        assert "Failed to extract text from file" in str(exc_info.value)
        assert "Extraction failed" in str(exc_info.value)


def test_import_resume_empty_text(import_service, temp_dir):
    """Test import when extracted text is empty."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=""):
        with pytest.raises(ImportError) as exc_info:
            import_service.import_resume(pdf_path)

        assert "No text could be extracted from the file" in str(exc_info.value)


def test_import_resume_whitespace_only_text(import_service, temp_dir):
    """Test import when extracted text is only whitespace."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value="   \n\t  "):
        with pytest.raises(ImportError) as exc_info:
            import_service.import_resume(pdf_path)

        assert "No text could be extracted from the file" in str(exc_info.value)


def test_import_resume_llm_parsing_error(import_service, mock_storage, temp_dir):
    """Test import when LLM parsing fails."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "Some resume text"

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", side_effect=Exception("LLM parsing failed")):
                with pytest.raises(ImportError) as exc_info:
                    import_service.import_resume(pdf_path)

                assert "Failed to parse resume" in str(exc_info.value)
                assert "LLM parsing failed" in str(exc_info.value)


def test_import_resume_model_creation_error(import_service, mock_storage, temp_dir):
    """Test import when model creation fails."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "Some resume text"
    parsed_data = {"bio": {}, "skills": [], "experiences": [], "projects": [], "stories": [], "educations": [], "links": []}

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data", side_effect=Exception("Model creation failed")):
                    with pytest.raises(ImportError) as exc_info:
                        import_service.import_resume(pdf_path)

                    assert "Failed to create models from parsed data" in str(exc_info.value)
                    assert "Model creation failed" in str(exc_info.value)


def test_import_resume_updates_existing_bio(import_service, mock_storage, temp_dir):
    """Test import updates existing bio."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "John Doe\nSoftware Engineer"
    parsed_data = {
        "bio": {"name": "John Doe", "location": "New York, NY"},
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "educations": [],
        "links": [],
    }

    existing_bio = Bio(name="John Doe", location="San Francisco, CA")
    new_bio = Bio(name="John Doe", location="New York, NY")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (new_bio, [], [], [], [], [], [])
                    mock_storage.load_bio.return_value = existing_bio

                    stats = import_service.import_resume(pdf_path)

                    assert stats["imported_bio"] == 0
                    assert stats["updated_bio"] == 1
                    mock_storage.save_bio.assert_called_once_with(new_bio)


def test_import_resume_skips_existing_skill(import_service, mock_storage, temp_dir):
    """Test import skips existing skill."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "Python, AWS"
    parsed_data = {
        "bio": {},
        "skills": [{"name": "Python", "category": "Programming"}],
        "experiences": [],
        "projects": [],
        "stories": [],
        "educations": [],
        "links": [],
    }

    existing_skill = Skill(name="Python", category="Programming", years=5, proficiency="Expert", related_experience=[], content="")
    new_skill = Skill(name="Python", category="Programming", years=0, proficiency="", related_experience=[], content="")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (None, [new_skill], [], [], [], [], [])
                    mock_storage.load_bio.return_value = None
                    mock_storage.load_skill.return_value = existing_skill

                    stats = import_service.import_resume(pdf_path)

                    assert stats["imported_skills"] == 0
                    assert stats["skipped_skills"] == 1
                    mock_storage.save_skill.assert_not_called()


def test_import_resume_imports_new_skill(import_service, mock_storage, temp_dir):
    """Test import imports new skill."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "Python, AWS"
    parsed_data = {
        "bio": {},
        "skills": [{"name": "AWS", "category": "Cloud"}],
        "experiences": [],
        "projects": [],
        "stories": [],
        "educations": [],
        "links": [],
    }

    new_skill = Skill(name="AWS", category="Cloud", years=0, proficiency="", related_experience=[], content="")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (None, [new_skill], [], [], [], [], [])
                    mock_storage.load_bio.return_value = None
                    mock_storage.load_skill.return_value = None

                    stats = import_service.import_resume(pdf_path)

                    assert stats["imported_skills"] == 1
                    assert stats["skipped_skills"] == 0
                    mock_storage.save_skill.assert_called_once_with(new_skill)


def test_import_resume_handles_all_data_types(import_service, mock_storage, temp_dir):
    """Test import handles all data types correctly."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "Resume content"
    parsed_data = {
        "bio": {"name": "John Doe"},
        "skills": [{"name": "Python"}],
        "experiences": [{"title": "Engineer"}],
        "projects": [{"name": "Project1"}],
        "stories": [{"title": "Story1"}],
        "educations": [{"name": "BS CS"}],
        "links": [{"name": "LinkedIn"}],
    }

    bio = Bio(name="John Doe", location="")
    skill = Skill(name="Python", category="", years=0, proficiency="", related_experience=[], content="")
    experience = Experience(title="Engineer", organization="", start_date="", end_date="", location="", related_skills=[], related_stories=[], content="")
    project = Project(name="Project1", description="", link="", content="")
    story = Story(title="Story1", context="", outcome="", content="")
    education = Education(name="BS CS", organization="", degree="", start_date="", end_date="", content="")
    link = Link(name="LinkedIn", description="", url="")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (bio, [skill], [experience], [project], [story], [education], [link])
                    mock_storage.load_bio.return_value = None
                    mock_storage.load_skill.return_value = None
                    mock_storage.load_experience.return_value = None
                    mock_storage.load_project.return_value = None
                    mock_storage.load_story.return_value = None
                    mock_storage.load_education.return_value = None
                    mock_storage.load_link.return_value = None

                    stats = import_service.import_resume(pdf_path)

                    assert stats["imported_bio"] == 1
                    assert stats["imported_skills"] == 1
                    assert stats["imported_experiences"] == 1
                    assert stats["imported_projects"] == 1
                    assert stats["imported_stories"] == 1
                    assert stats["imported_educations"] == 1
                    assert stats["imported_links"] == 1

                    mock_storage.save_bio.assert_called_once()
                    mock_storage.save_skill.assert_called_once()
                    mock_storage.save_experience.assert_called_once()
                    mock_storage.save_project.assert_called_once()
                    mock_storage.save_story.assert_called_once()
                    mock_storage.save_education.assert_called_once()
                    mock_storage.save_link.assert_called_once()


def test_import_resume_skips_all_existing_items(import_service, mock_storage, temp_dir):
    """Test import skips all existing items."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "Resume content"
    parsed_data = {
        "bio": {"name": "John Doe"},
        "skills": [{"name": "Python"}],
        "experiences": [{"title": "Engineer"}],
        "projects": [{"name": "Project1"}],
        "stories": [{"title": "Story1"}],
        "educations": [{"name": "BS CS"}],
        "links": [{"name": "LinkedIn"}],
    }

    bio = Bio(name="John Doe", location="")
    skill = Skill(name="Python", category="", years=0, proficiency="", related_experience=[], content="")
    experience = Experience(title="Engineer", organization="", start_date="", end_date="", location="", related_skills=[], related_stories=[], content="")
    project = Project(name="Project1", description="", link="", content="")
    story = Story(title="Story1", context="", outcome="", content="")
    education = Education(name="BS CS", organization="", degree="", start_date="", end_date="", content="")
    link = Link(name="LinkedIn", description="", url="")

    existing_bio = Bio(name="John Doe", location="SF")
    existing_skill = Skill(name="Python", category="", years=0, proficiency="", related_experience=[], content="")
    existing_experience = Experience(title="Engineer", organization="", start_date="", end_date="", location="", related_skills=[], related_stories=[], content="")
    existing_project = Project(name="Project1", description="", link="", content="")
    existing_story = Story(title="Story1", context="", outcome="", content="")
    existing_education = Education(name="BS CS", organization="", degree="", start_date="", end_date="", content="")
    existing_link = Link(name="LinkedIn", description="", url="")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (bio, [skill], [experience], [project], [story], [education], [link])
                    mock_storage.load_bio.return_value = existing_bio
                    mock_storage.load_skill.return_value = existing_skill
                    mock_storage.load_experience.return_value = existing_experience
                    mock_storage.load_project.return_value = existing_project
                    mock_storage.load_story.return_value = existing_story
                    mock_storage.load_education.return_value = existing_education
                    mock_storage.load_link.return_value = existing_link

                    stats = import_service.import_resume(pdf_path)

                    assert stats["imported_bio"] == 0
                    assert stats["updated_bio"] == 1  # Bio is always updated if it exists
                    assert stats["skipped_skills"] == 1
                    assert stats["skipped_experiences"] == 1
                    assert stats["skipped_projects"] == 1
                    assert stats["skipped_stories"] == 1
                    assert stats["skipped_educations"] == 1
                    assert stats["skipped_links"] == 1

                    # Bio should be saved (updated)
                    mock_storage.save_bio.assert_called_once()
                    # Other items should not be saved
                    mock_storage.save_skill.assert_not_called()
                    mock_storage.save_experience.assert_not_called()
                    mock_storage.save_project.assert_not_called()
                    mock_storage.save_story.assert_not_called()
                    mock_storage.save_education.assert_not_called()
                    mock_storage.save_link.assert_not_called()


def test_import_resume_mixed_new_and_existing(import_service, mock_storage, temp_dir):
    """Test import with mix of new and existing items."""
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.write_text("dummy content")
    extracted_text = "Resume content"
    parsed_data = {
        "bio": {},
        "skills": [{"name": "Python"}, {"name": "AWS"}],
        "experiences": [{"title": "Engineer"}],
        "projects": [],
        "stories": [],
        "educations": [],
        "links": [],
    }

    skill1 = Skill(name="Python", category="", years=0, proficiency="", related_experience=[], content="")
    skill2 = Skill(name="AWS", category="", years=0, proficiency="", related_experience=[], content="")
    experience = Experience(title="Engineer", organization="", start_date="", end_date="", location="", related_skills=[], related_stories=[], content="")
    existing_skill = Skill(name="Python", category="", years=0, proficiency="", related_experience=[], content="")

    with patch("cveasy.services.import_service.extract_text_from_pdf", return_value=extracted_text):
        with patch("cveasy.services.import_service.get_ai_provider") as mock_get_provider:
            with patch("cveasy.services.import_service.parse_resume_with_llm", return_value=parsed_data):
                with patch("cveasy.services.import_service.create_models_from_parsed_data") as mock_create:
                    mock_create.return_value = (None, [skill1, skill2], [experience], [], [], [], [])
                    mock_storage.load_bio.return_value = None
                    mock_storage.load_skill.side_effect = [existing_skill, None]  # First exists, second doesn't
                    mock_storage.load_experience.return_value = None

                    stats = import_service.import_resume(pdf_path)

                    assert stats["skipped_skills"] == 1
                    assert stats["imported_skills"] == 1
                    assert stats["imported_experiences"] == 1
                    assert stats["skipped_experiences"] == 0

                    # Should save AWS (new) but not Python (existing)
                    assert mock_storage.save_skill.call_count == 1
                    mock_storage.save_skill.assert_called_with(skill2)
