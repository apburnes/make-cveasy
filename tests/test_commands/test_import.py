"""Tests for import command."""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typer.testing import CliRunner

from cveasy.cli import app


def test_import_command_pdf_success(temp_dir, storage):
    """Test successful import from PDF file."""
    runner = CliRunner()

    # Create a mock PDF file
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    # Mock parsed data
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
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            # Mock project path finding
            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                assert "Import complete" in result.stdout
                assert "1 imported" in result.stdout or "imported" in result.stdout


def test_import_command_docx_success(temp_dir, storage):
    """Test successful import from DOCX file."""
    runner = CliRunner()

    # Create a mock DOCX file
    docx_path = temp_dir / "resume.docx"
    docx_path.touch()

    parsed_data = {
        "skills": [{"name": "JavaScript"}],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    with patch("cveasy.commands.import.extract_text_from_docx") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(docx_path)])

                assert result.exit_code == 0
                assert "Import complete" in result.stdout


def test_import_command_file_not_found(temp_dir):
    """Test import command with non-existent file."""
    runner = CliRunner()

    pdf_path = temp_dir / "nonexistent.pdf"

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["import", "-f", str(pdf_path)])

        assert result.exit_code == 1
        assert "not found" in result.stderr.lower() or "Error" in result.stderr


def test_import_command_unsupported_format(temp_dir):
    """Test import command with unsupported file format."""
    runner = CliRunner()

    txt_path = temp_dir / "resume.txt"
    txt_path.touch()

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["import", "-f", str(txt_path)])

        assert result.exit_code == 1
        assert "Unsupported file type" in result.stderr or "Error" in result.stderr


def test_import_command_skips_duplicates(temp_dir, storage):
    """Test import command skips existing entries."""
    runner = CliRunner()

    # Create existing skill
    from cveasy.models.skill import Skill
    existing_skill = Skill(name="Python", category="Language")
    storage.save_skill(existing_skill)

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    parsed_data = {
        "skills": [
            {"name": "Python", "category": "Programming Language"}  # Duplicate
        ],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                assert "skipped" in result.stdout.lower()


def test_import_command_empty_text(temp_dir):
    """Test import command with empty extracted text."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = ""  # Empty text

        with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 1
            assert "No text" in result.stderr or "Error" in result.stderr


def test_import_command_llm_parsing_error(temp_dir):
    """Test import command handles LLM parsing errors."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.side_effect = ValueError("LLM parsing failed")
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 1
                assert "Error" in result.stderr or "Failed" in result.stderr


def test_import_command_text_extraction_error(temp_dir):
    """Test import command handles text extraction errors."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.side_effect = ValueError("Failed to extract text")

        with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 1
            assert "Error" in result.stderr or "Failed" in result.stderr


def test_import_command_imports_all_types(temp_dir, storage):
    """Test import command imports all data types."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    parsed_data = {
        "skills": [{"name": "Python"}],
        "experiences": [
            {
                "title": "Engineer",
                "organization": "Corp",
                "content": "Worked on projects"
            }
        ],
        "projects": [{"name": "Project1", "description": "A project"}],
        "stories": [{"title": "Achievement", "content": "Did something"}],
        "education": [{"name": "Bachelor of Science", "organization": "University"}],
        "links": [{"name": "LinkedIn", "description": "Professional profile", "url": "https://linkedin.com/in/user"}],
    }

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                # Verify all types are mentioned in output
                assert "Skills" in result.stdout or "skills" in result.stdout.lower()
                assert "Experiences" in result.stdout or "experiences" in result.stdout.lower()
                assert "Projects" in result.stdout or "projects" in result.stdout.lower()
                assert "Stories" in result.stdout or "stories" in result.stdout.lower()
                assert "Education" in result.stdout or "education" in result.stdout.lower()
                assert "Links" in result.stdout or "links" in result.stdout.lower()


def test_import_command_no_new_entries(temp_dir, storage):
    """Test import command when all entries already exist."""
    runner = CliRunner()

    # Create existing entries
    from cveasy.models.skill import Skill
    from cveasy.models.experience import Experience

    existing_skill = Skill(name="Python")
    storage.save_skill(existing_skill)

    existing_exp = Experience(title="Engineer", organization="Corp")
    storage.save_experience(existing_exp)

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    parsed_data = {
        "skills": [{"name": "Python"}],  # Duplicate
        "experiences": [
            {"title": "Engineer", "organization": "Corp"}  # Duplicate
        ],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [],
    }

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                # Should warn about no new entries
                assert "No new entries" in result.stdout or "0 imported" in result.stdout


def test_import_command_imports_links(temp_dir, storage):
    """Test import command imports links correctly."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    parsed_data = {
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [
            {"name": "LinkedIn", "description": "Professional profile", "url": "https://linkedin.com/in/user"},
            {"name": "GitHub", "description": "Code repository", "url": "https://github.com/user"},
        ],
    }

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                assert "Import complete" in result.stdout
                assert "Links" in result.stdout or "links" in result.stdout.lower()
                assert "2 imported" in result.stdout or "imported" in result.stdout

                # Verify links were saved
                from cveasy.models.link import Link
                linkedin_link = storage.load_link("LinkedIn")
                assert linkedin_link is not None
                assert linkedin_link.name == "LinkedIn"
                assert linkedin_link.url == "https://linkedin.com/in/user"

                github_link = storage.load_link("GitHub")
                assert github_link is not None
                assert github_link.name == "GitHub"
                assert github_link.url == "https://github.com/user"


def test_import_command_imports_bio(temp_dir, storage):
    """Test import command imports bio correctly."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

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

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                assert "Import complete" in result.stdout
                assert "Bio" in result.stdout or "bio" in result.stdout.lower()
                assert "1 imported" in result.stdout or "imported" in result.stdout

                # Verify bio was saved
                from cveasy.models.bio import Bio
                bio = storage.load_bio()
                assert bio is not None
                assert bio.name == "John Doe"
                assert bio.location == "San Francisco, CA"


def test_import_command_updates_existing_bio(temp_dir, storage):
    """Test import command updates existing bio."""
    runner = CliRunner()

    # Create existing bio
    from cveasy.models.bio import Bio
    existing_bio = Bio(name="Jane Doe", location="New York, NY")
    storage.save_bio(existing_bio)

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

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

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                assert "updated" in result.stdout.lower() or "imported" in result.stdout.lower()

                # Verify existing bio was updated
                bio = storage.load_bio()
                assert bio is not None
                assert bio.name == "John Doe"  # Bio was updated
                assert bio.location == "San Francisco, CA"


def test_import_command_skips_duplicate_links(temp_dir, storage):
    """Test import command skips existing links."""
    runner = CliRunner()

    # Create existing link
    from cveasy.models.link import Link
    existing_link = Link(name="LinkedIn", description="Professional profile", url="https://linkedin.com/in/user")
    storage.save_link(existing_link)

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    parsed_data = {
        "skills": [],
        "experiences": [],
        "projects": [],
        "stories": [],
        "education": [],
        "links": [
            {"name": "LinkedIn", "description": "Professional profile", "url": "https://linkedin.com/in/user"}  # Duplicate
        ],
    }

    with patch("cveasy.commands.import.extract_text_from_pdf") as mock_extract:
        mock_extract.return_value = "Sample resume text"

        with patch("cveasy.commands.import.get_ai_provider") as mock_get_provider:
            mock_provider = Mock()
            mock_provider.generate.return_value = json.dumps(parsed_data)
            mock_get_provider.return_value = mock_provider

            with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
                result = runner.invoke(app, ["import", "-f", str(pdf_path)])

                assert result.exit_code == 0
                assert "skipped" in result.stdout.lower()
