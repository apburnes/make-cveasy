"""Tests for export command."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cveasy.cli import app


def test_export_with_application_flag_pdf(temp_dir, storage):
    """Test export application resume to PDF using --application."""
    runner = CliRunner()

    # Create application directory and resume
    application_id = "test-app-20240115"
    app_dir = temp_dir / "applications" / application_id
    app_dir.mkdir(parents=True, exist_ok=True)
    resume_file = app_dir / "resume.md"
    resume_file.write_text("# Test Resume\n\n## Experience\n\nSoftware Engineer")

    output_path = app_dir / "resume.pdf"

    mock_service = MagicMock()
    mock_service.export_application_resume.return_value = output_path

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, ["export", "--application", application_id, "--format", "pdf"])

            assert result.exit_code == 0
            assert "Exporting resume to PDF" in result.stdout
            assert "exported to" in result.stdout
            mock_service.export_application_resume.assert_called_once_with(application_id, None, "pdf")


def test_export_with_application_flag_docx(temp_dir, storage):
    """Test export application resume to DOCX using --application."""
    runner = CliRunner()

    # Create application directory and resume
    application_id = "test-app-20240115"
    app_dir = temp_dir / "applications" / application_id
    app_dir.mkdir(parents=True, exist_ok=True)
    resume_file = app_dir / "resume.md"
    resume_file.write_text("# Test Resume\n\n## Experience\n\nSoftware Engineer")

    output_path = app_dir / "resume.docx"

    mock_service = MagicMock()
    mock_service.export_application_resume.return_value = output_path

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, ["export", "--application", application_id, "--format", "docx"])

            assert result.exit_code == 0
            assert "Exporting resume to DOCX" in result.stdout
            assert "exported to" in result.stdout
            mock_service.export_application_resume.assert_called_once_with(application_id, None, "docx")


def test_export_with_file_flag(temp_dir, storage):
    """Test export using --file flag."""
    runner = CliRunner()

    # Create resume file
    resume_file = temp_dir / "resume.md"
    resume_file.write_text("# Test Resume\n\n## Experience\n\nSoftware Engineer")

    output_path = temp_dir / "resume.pdf"

    mock_service = MagicMock()
    mock_service.export_file_resume.return_value = output_path

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, ["export", "--file", str(resume_file)])

            assert result.exit_code == 0
            assert "Exporting resume to PDF" in result.stdout
            assert "exported to" in result.stdout
            mock_service.export_file_resume.assert_called_once()


def test_export_application_not_found(temp_dir, storage):
    """Test export when application doesn't exist."""
    runner = CliRunner()

    application_id = "nonexistent-app"

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.export_application_resume.side_effect = NotFoundError("Resume not found for application")

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, ["export", "--application", application_id])

            assert result.exit_code == 1
            assert "Resume not found for application" in result.stderr


def test_export_file_not_found(temp_dir, storage):
    """Test export when file doesn't exist."""
    runner = CliRunner()

    nonexistent_file = temp_dir / "nonexistent.md"

    from cveasy.exceptions import NotFoundError

    mock_service = MagicMock()
    mock_service.export_file_resume.side_effect = NotFoundError("Resume file not found")

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, ["export", "--file", str(nonexistent_file)])

            assert result.exit_code == 1
            assert "Resume file not found" in result.stderr


def test_export_multiple_sources_error(temp_dir, storage):
    """Test export when both --application and --file are provided."""
    runner = CliRunner()

    resume_file = temp_dir / "resume.md"
    resume_file.write_text("# Test Resume")

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["export", "--application", "test-app", "--file", str(resume_file)])

        assert result.exit_code == 1
        assert "only specify one resume source" in result.stderr.lower()


def test_export_no_source_error(temp_dir, storage):
    """Test export when neither flag is provided."""
    runner = CliRunner()

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["export"])

        assert result.exit_code == 1
        assert "must specify a resume source" in result.stderr.lower()


def test_export_application_with_custom_output(temp_dir, storage):
    """Test export application resume with custom output path."""
    runner = CliRunner()

    # Create application directory and resume
    application_id = "test-app-20240115"
    app_dir = temp_dir / "applications" / application_id
    app_dir.mkdir(parents=True, exist_ok=True)
    resume_file = app_dir / "resume.md"
    resume_file.write_text("# Test Resume\n\n## Experience\n\nSoftware Engineer")

    custom_output = temp_dir / "custom-resume.pdf"

    mock_service = MagicMock()
    mock_service.export_application_resume.return_value = custom_output

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, [
                "export",
                "--application", application_id,
                "--output", str(custom_output)
            ])

            assert result.exit_code == 0
            assert "Exporting resume to PDF" in result.stdout
            mock_service.export_application_resume.assert_called_once_with(application_id, custom_output, "pdf")


def test_export_file_with_custom_output(temp_dir, storage):
    """Test export file with custom output path."""
    runner = CliRunner()

    # Create resume file
    resume_file = temp_dir / "resume.md"
    resume_file.write_text("# Test Resume\n\n## Experience\n\nSoftware Engineer")

    custom_output = temp_dir / "custom-resume.pdf"

    mock_service = MagicMock()
    mock_service.export_file_resume.return_value = custom_output

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, [
                "export",
                "--file", str(resume_file),
                "--output", str(custom_output)
            ])

            assert result.exit_code == 0
            assert "Exporting resume to PDF" in result.stdout
            mock_service.export_file_resume.assert_called_once()
            # Verify custom output path was used
            call_args = mock_service.export_file_resume.call_args
            assert call_args[0][1] == custom_output


def test_export_application_with_relative_file_path(temp_dir, storage):
    """Test export with --file using relative path."""
    runner = CliRunner()

    # Create resume file
    resume_file = temp_dir / "resume.md"
    resume_file.write_text("# Test Resume\n\n## Experience\n\nSoftware Engineer")

    output_path = temp_dir / "resume.pdf"

    mock_service = MagicMock()
    mock_service.export_file_resume.return_value = output_path

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, ["export", "--file", "resume.md"])

            assert result.exit_code == 0
            assert "Exporting resume to PDF" in result.stdout
            mock_service.export_file_resume.assert_called_once()


def test_export_application_output_next_to_source(temp_dir, storage):
    """Test export application resume saves output next to source file."""
    runner = CliRunner()

    # Create application directory and resume
    application_id = "test-app-20240115"
    app_dir = temp_dir / "applications" / application_id
    app_dir.mkdir(parents=True, exist_ok=True)
    resume_file = app_dir / "resume.md"
    resume_file.write_text("# Test Resume\n\n## Experience\n\nSoftware Engineer")

    expected_output = app_dir / "resume.pdf"

    mock_service = MagicMock()
    mock_service.export_application_resume.return_value = expected_output

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, ["export", "--application", application_id])

            assert result.exit_code == 0
            mock_service.export_application_resume.assert_called_once_with(application_id, None, "pdf")


def test_export_output_extension_handling_pdf(temp_dir, storage):
    """Test export handles output file extension correctly for PDF."""
    runner = CliRunner()

    resume_file = temp_dir / "resume.md"
    resume_file.write_text("# Test Resume")

    # Test with no extension
    custom_output = temp_dir / "output"
    expected_output = temp_dir / "output.pdf"

    mock_service = MagicMock()
    mock_service.export_file_resume.return_value = expected_output

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, [
                "export",
                "--file", str(resume_file),
                "--output", str(custom_output),
                "--format", "pdf"
            ])

            assert result.exit_code == 0
            mock_service.export_file_resume.assert_called_once()
            call_args = mock_service.export_file_resume.call_args
            # The service handles extension, so verify it was called correctly
            assert call_args[0][2] == "pdf"


def test_export_output_extension_handling_docx(temp_dir, storage):
    """Test export handles output file extension correctly for DOCX."""
    runner = CliRunner()

    resume_file = temp_dir / "resume.md"
    resume_file.write_text("# Test Resume")

    # Test with wrong extension
    custom_output = temp_dir / "output.pdf"
    expected_output = temp_dir / "output.docx"

    mock_service = MagicMock()
    mock_service.export_file_resume.return_value = expected_output

    with patch("cveasy.commands.export.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.export.ExportService", return_value=mock_service):
            result = runner.invoke(app, [
                "export",
                "--file", str(resume_file),
                "--output", str(custom_output),
                "--format", "docx"
            ])

            assert result.exit_code == 0
            mock_service.export_file_resume.assert_called_once()
            call_args = mock_service.export_file_resume.call_args
            # The service handles extension, so verify it was called correctly
            assert call_args[0][2] == "docx"
