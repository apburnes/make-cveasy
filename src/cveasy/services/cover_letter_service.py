"""Service for cover letter generation and management."""

from pathlib import Path
from typing import Optional

from cveasy.storage import MarkdownStorage
from cveasy.ai import ResumeGenerator
from cveasy.exceptions import NotFoundError, ResumeGenerationError


class CoverLetterService:
    """Service for managing cover letter generation."""

    def __init__(self, project_path: Path):
        """
        Initialize cover letter service.

        Args:
            project_path: Path to the project directory.
        """
        self.storage = MarkdownStorage(project_path)
        self.generator = ResumeGenerator()

    def generate_cover_letter(self, application_id: str, reason: Optional[str] = None) -> Path:
        """
        Generate a personalized cover letter for a specific job application.

        Args:
            application_id: ID of the job application.
            reason: Optional reason for interest in the job.

        Returns:
            Path to the saved cover letter file.

        Raises:
            NotFoundError: If application not found.
            ResumeGenerationError: If generation fails.
        """
        job = self.storage.load_job(application_id)
        if not job:
            raise NotFoundError(
                f"Job application '{application_id}' not found. "
                f"Create it first with: cveasy add job --name <name>"
            )

        try:
            bio = self.storage.load_bio()
            skills = self.storage.list_skills()
            experiences = self.storage.list_experiences()
            stories = self.storage.list_stories()
            links = self.storage.list_links()
            projects = self.storage.list_projects()
            educations = self.storage.list_educations()

            cover_letter_content = self.generator.generate_cover_letter(
                job=job,
                skills=skills,
                experiences=experiences,
                stories=stories,
                links=links,
                projects=projects,
                educations=educations,
                bio=bio,
                reason=reason,
            )

            return self.storage.save_cover_letter(cover_letter_content, application_id=application_id)
        except NotFoundError:
            raise
        except Exception as e:
            raise ResumeGenerationError(
                f"Failed to generate cover letter for application '{application_id}': {e}"
            ) from e
