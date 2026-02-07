"""Service for exporting resumes to PDF/DOCX formats."""

from pathlib import Path
from typing import Optional

from cveasy.storage import MarkdownStorage
from cveasy.export import export_to_pdf, export_to_word
from cveasy.exceptions import NotFoundError, ExportError, ValidationError


class ExportService:
    """Service for exporting resumes."""

    def __init__(self, project_path: Path):
        """
        Initialize export service.

        Args:
            project_path: Path to the project directory.
        """
        self.storage = MarkdownStorage(project_path)
        self.project_path = project_path

    def export_resume(self, resume_content: str, output_path: Path, format: str) -> Path:
        """
        Export resume content to a file.

        Args:
            resume_content: Resume content in markdown.
            output_path: Output file path.
            format: Export format ('pdf' or 'docx').

        Returns:
            Path to the exported file.

        Raises:
            ValidationError: If format is invalid.
            ExportError: If export fails.
        """
        format_lower = format.lower()
        if format_lower not in ["pdf", "docx"]:
            raise ValidationError(f"Unknown format '{format}'. Use 'pdf' or 'docx'.")

        try:
            if format_lower == "pdf":
                return export_to_pdf(resume_content, output_path)
            else:
                return export_to_word(resume_content, output_path)
        except Exception as e:
            raise ExportError(f"Failed to export resume: {e}") from e

    def export_application_resume(
        self, application_id: str, output_path: Optional[Path] = None, format: str = "pdf"
    ) -> Path:
        """
        Export an application's resume to a file.

        Args:
            application_id: ID of the application.
            output_path: Optional output file path. If None, saves next to resume.
            format: Export format ('pdf' or 'docx').

        Returns:
            Path to the exported file.

        Raises:
            NotFoundError: If application or resume not found.
            ValidationError: If format is invalid.
            ExportError: If export fails.
        """
        resume_content = self.storage.load_resume(application_id=application_id)
        if not resume_content:
            raise NotFoundError(
                f"Resume not found for application '{application_id}'. "
                f"Generate it first with: cveasy generate --application {application_id}"
            )

        if output_path is None:
            resume_path = self.project_path / "applications" / application_id / "resume.md"
            if format.lower() == "pdf":
                output_path = resume_path.with_suffix(".pdf")
            else:
                output_path = resume_path.with_suffix(".docx")

        return self.export_resume(resume_content, output_path, format)

    def export_general_resume(
        self, output_path: Optional[Path] = None, format: str = "pdf"
    ) -> Path:
        """
        Export the most recent general resume to a file.

        Args:
            output_path: Optional output file path. If None, saves next to the
                general resume file in the resume directory.
            format: Export format ('pdf' or 'docx').

        Returns:
            Path to the exported file.

        Raises:
            NotFoundError: If no general resume found.
            ValidationError: If format is invalid.
            ExportError: If export fails.
        """
        resume_content = self.storage.load_resume()
        if not resume_content:
            raise NotFoundError(
                "No general resume found. Generate one with: cveasy generate --no-select"
            )

        if output_path is None:
            resume_dir = self.project_path / "resume"
            resumes = sorted(resume_dir.glob("resume-*.md"), reverse=True)
            if not resumes:
                raise NotFoundError(
                    "No general resume found. Generate one with: cveasy generate --no-select"
                )
            source_path = resumes[0]
            if format.lower() == "pdf":
                output_path = source_path.with_suffix(".pdf")
            else:
                output_path = source_path.with_suffix(".docx")

        return self.export_resume(resume_content, output_path, format)

    def export_file_resume(
        self, file_path: Path, output_path: Optional[Path] = None, format: str = "pdf"
    ) -> Path:
        """
        Export a resume from a markdown file.

        Args:
            file_path: Path to the resume markdown file.
            output_path: Optional output file path. If None, saves next to source file.
            format: Export format ('pdf' or 'docx').

        Returns:
            Path to the exported file.

        Raises:
            NotFoundError: If file not found.
            ValidationError: If format is invalid.
            ExportError: If export fails.
        """
        if not file_path.exists():
            raise NotFoundError(f"Resume file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                resume_content = f.read()
        except Exception as e:
            raise ExportError(f"Failed to read resume file: {e}") from e

        if output_path is None:
            if format.lower() == "pdf":
                output_path = file_path.with_suffix(".pdf")
            else:
                output_path = file_path.with_suffix(".docx")

        return self.export_resume(resume_content, output_path, format)
