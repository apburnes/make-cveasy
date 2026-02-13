"""Service for importing resume data from PDF/DOCX files."""

import logging
from pathlib import Path
from typing import Dict

from cveasy.storage import MarkdownStorage
from cveasy.parsing import (
    extract_text_from_pdf,
    extract_text_from_docx,
    parse_resume_with_llm,
    create_models_from_parsed_data,
)
from cveasy.ai.providers import get_ai_provider
from cveasy.exceptions import DataImportError, ValidationError

logger = logging.getLogger(__name__)


class ImportService:
    """Service for importing resume data from files."""

    def __init__(self, project_path: Path):
        """
        Initialize import service.

        Args:
            project_path: Path to the project directory.
        """
        self.storage = MarkdownStorage(project_path)

    def import_resume(self, file_path: Path) -> Dict[str, int]:
        """
        Import resume data from a PDF or DOCX file.

        Args:
            file_path: Path to the resume file.

        Returns:
            Dictionary with import statistics.

        Raises:
            ValidationError: If file is invalid or unsupported.
            ImportError: If import fails.
        """
        # Validate file exists
        if not file_path.exists():
            raise ValidationError(f"File not found: {file_path}")

        # Validate file type
        file_ext = file_path.suffix.lower()
        if file_ext not in [".pdf", ".docx"]:
            raise ValidationError(
                f"Unsupported file type '{file_ext}'. Only PDF and DOCX files are supported."
            )

        # Extract text
        logger.debug("Importing resume from %s", file_path)
        try:
            if file_ext == ".pdf":
                text = extract_text_from_pdf(file_path)
            else:
                text = extract_text_from_docx(file_path)
        except (DataImportError, ValidationError):
            raise
        except (OSError, ValueError, KeyError) as e:
            raise DataImportError(f"Failed to extract text from file: {e}") from e

        if not text.strip():
            raise DataImportError("No text could be extracted from the file.")

        logger.debug("Extracted %d chars of text", len(text))

        # Parse with LLM
        try:
            provider = get_ai_provider()
            parsed_data = parse_resume_with_llm(text, provider)
        except DataImportError:
            raise
        except (ValueError, OSError) as e:
            raise DataImportError(f"Failed to parse resume: {e}") from e

        # Create model objects
        try:
            bio, skills, experiences, projects, stories, educations, links = (
                create_models_from_parsed_data(parsed_data)
            )
        except (ValueError, TypeError, KeyError) as e:
            raise DataImportError(f"Failed to create models from parsed data: {e}") from e

        # Import statistics
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
            "skipped_links": 0,
        }

        # Save bio (always update if bio exists in parsed data)
        if bio:
            existing = self.storage.load_bio()
            if existing:
                self.storage.save_bio(bio)
                stats["updated_bio"] = 1
            else:
                self.storage.save_bio(bio)
                stats["imported_bio"] = 1

        # Save skills
        for skill in skills:
            existing = self.storage.load_skill(skill.name)
            if existing:
                stats["skipped_skills"] += 1
            else:
                self.storage.save_skill(skill)
                stats["imported_skills"] += 1

        # Save experiences
        for experience in experiences:
            existing = self.storage.load_experience(experience.title)
            if existing:
                stats["skipped_experiences"] += 1
            else:
                self.storage.save_experience(experience)
                stats["imported_experiences"] += 1

        # Save projects
        for project in projects:
            existing = self.storage.load_project(project.name)
            if existing:
                stats["skipped_projects"] += 1
            else:
                self.storage.save_project(project)
                stats["imported_projects"] += 1

        # Save stories
        for story in stories:
            existing = self.storage.load_story(story.title)
            if existing:
                stats["skipped_stories"] += 1
            else:
                self.storage.save_story(story)
                stats["imported_stories"] += 1

        # Save educations
        for education in educations:
            existing = self.storage.load_education(education.name)
            if existing:
                stats["skipped_educations"] += 1
            else:
                self.storage.save_education(education)
                stats["imported_educations"] += 1

        # Save links
        for link in links:
            existing = self.storage.load_link(link.name)
            if existing:
                stats["skipped_links"] += 1
            else:
                self.storage.save_link(link)
                stats["imported_links"] += 1

        logger.debug("Import complete: %s", stats)
        return stats
