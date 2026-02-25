"""Tests for import command."""

from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cveasy.cli import app


def test_import_command_pdf_success(temp_dir, storage):
    """Test successful import from PDF file."""
    runner = CliRunner()

    # Create a mock PDF file
    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    # Mock import statistics
    stats = {
        "imported_bio": 0,
        "updated_bio": 0,
        "imported_skills": 1,
        "skipped_skills": 0,
        "imported_experiences": 1,
        "skipped_experiences": 0,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 0,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 0
            assert "Import complete" in result.stdout
            assert "1 imported" in result.stdout or "imported" in result.stdout
            mock_service.import_resume.assert_called_once_with(pdf_path)


def test_import_command_docx_success(temp_dir, storage):
    """Test successful import from DOCX file."""
    runner = CliRunner()

    # Create a mock DOCX file
    docx_path = temp_dir / "resume.docx"
    docx_path.touch()

    stats = {
        "imported_bio": 0,
        "updated_bio": 0,
        "imported_skills": 1,
        "skipped_skills": 0,
        "imported_experiences": 0,
        "skipped_experiences": 0,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 0,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(docx_path)])

            assert result.exit_code == 0
            assert "Import complete" in result.stdout


def test_import_command_file_not_found(temp_dir):
    """Test import command with non-existent file."""
    runner = CliRunner()

    pdf_path = temp_dir / "nonexistent.pdf"

    from cveasy.exceptions import ValidationError

    mock_service = MagicMock()
    mock_service.import_resume.side_effect = ValidationError(f"File not found: {pdf_path}")

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 1
            assert "not found" in result.stderr.lower() or "Error" in result.stderr


def test_import_command_unsupported_format(temp_dir):
    """Test import command with unsupported file format."""
    runner = CliRunner()

    txt_path = temp_dir / "resume.txt"
    txt_path.touch()

    from cveasy.exceptions import ValidationError

    mock_service = MagicMock()
    mock_service.import_resume.side_effect = ValidationError(
        "Unsupported file type '.txt'. Only PDF and DOCX files are supported."
    )

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
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

    stats = {
        "imported_bio": 0,
        "updated_bio": 0,
        "imported_skills": 0,
        "skipped_skills": 1,
        "imported_experiences": 0,
        "skipped_experiences": 0,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 0,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 0
            assert "skipped" in result.stdout.lower()


def test_import_command_empty_text(temp_dir):
    """Test import command with empty extracted text."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    from cveasy.exceptions import DataImportError

    mock_service = MagicMock()
    mock_service.import_resume.side_effect = DataImportError(
        "No text could be extracted from the file."
    )

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 1
            assert "No text" in result.stderr or "Error" in result.stderr


def test_import_command_llm_parsing_error(temp_dir):
    """Test import command handles LLM parsing errors."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    from cveasy.exceptions import DataImportError

    mock_service = MagicMock()
    mock_service.import_resume.side_effect = DataImportError(
        "Failed to parse resume: LLM parsing failed"
    )

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 1
            assert "Error" in result.stderr or "Failed" in result.stderr


def test_import_command_text_extraction_error(temp_dir):
    """Test import command handles text extraction errors."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    from cveasy.exceptions import DataImportError

    mock_service = MagicMock()
    mock_service.import_resume.side_effect = DataImportError(
        "Failed to extract text from file: Failed to extract text"
    )

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 1
            assert "Error" in result.stderr or "Failed" in result.stderr


def test_import_command_imports_all_types(temp_dir, storage):
    """Test import command imports all data types."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    stats = {
        "imported_bio": 0,
        "updated_bio": 0,
        "imported_skills": 1,
        "skipped_skills": 0,
        "imported_experiences": 1,
        "skipped_experiences": 0,
        "imported_projects": 1,
        "skipped_projects": 0,
        "imported_stories": 1,
        "skipped_stories": 0,
        "imported_educations": 1,
        "skipped_educations": 0,
        "imported_links": 1,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
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

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    stats = {
        "imported_bio": 0,
        "updated_bio": 0,
        "imported_skills": 0,
        "skipped_skills": 1,
        "imported_experiences": 0,
        "skipped_experiences": 1,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 0,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 0
            # Should warn about no new entries
            assert "No new entries" in result.stdout or "0 imported" in result.stdout


def test_import_command_imports_links(temp_dir, storage):
    """Test import command imports links correctly."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    stats = {
        "imported_bio": 0,
        "updated_bio": 0,
        "imported_skills": 0,
        "skipped_skills": 0,
        "imported_experiences": 0,
        "skipped_experiences": 0,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 2,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 0
            assert "Import complete" in result.stdout
            assert "Links" in result.stdout or "links" in result.stdout.lower()
            assert "2 imported" in result.stdout or "imported" in result.stdout


def test_import_command_imports_bio(temp_dir, storage):
    """Test import command imports bio correctly."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    stats = {
        "imported_bio": 1,
        "updated_bio": 0,
        "imported_skills": 0,
        "skipped_skills": 0,
        "imported_experiences": 0,
        "skipped_experiences": 0,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 0,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 0
            assert "Import complete" in result.stdout
            assert "Bio" in result.stdout or "bio" in result.stdout.lower()
            assert "1 imported" in result.stdout or "imported" in result.stdout


def test_import_command_updates_existing_bio(temp_dir, storage):
    """Test import command updates existing bio."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    stats = {
        "imported_bio": 0,
        "updated_bio": 1,
        "imported_skills": 0,
        "skipped_skills": 0,
        "imported_experiences": 0,
        "skipped_experiences": 0,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 0,
        "skipped_links": 0,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 0
            assert "updated" in result.stdout.lower() or "imported" in result.stdout.lower()


def test_import_command_skips_duplicate_links(temp_dir, storage):
    """Test import command skips existing links."""
    runner = CliRunner()

    pdf_path = temp_dir / "resume.pdf"
    pdf_path.touch()

    stats = {
        "imported_bio": 0,
        "updated_bio": 0,
        "imported_skills": 0,
        "skipped_skills": 0,
        "imported_experiences": 0,
        "skipped_experiences": 0,
        "imported_projects": 0,
        "skipped_projects": 0,
        "imported_stories": 0,
        "skipped_stories": 0,
        "imported_educations": 0,
        "skipped_educations": 0,
        "imported_links": 0,
        "skipped_links": 1,
    }

    mock_service = MagicMock()
    mock_service.import_resume.return_value = stats

    with patch("cveasy.commands.import.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.import.ImportService", return_value=mock_service):
            result = runner.invoke(app, ["import", "-f", str(pdf_path)])

            assert result.exit_code == 0
            assert "skipped" in result.stdout.lower()
