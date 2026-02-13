"""Service for cover letter generation and management."""

import logging
from pathlib import Path
from typing import Optional

from cveasy.storage import MarkdownStorage
from cveasy.ai import ResumeGenerator
from cveasy.exceptions import NotFoundError, ResumeGenerationError

logger = logging.getLogger(__name__)


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
            logger.debug("Generating cover letter for application '%s'", application_id)
            data = self.storage.load_all_candidate_data()

            cover_letter_content = self.generator.generate_cover_letter(
                job=job, **data, reason=reason,
            )

            return self.storage.save_cover_letter(
                cover_letter_content, application_id=application_id
            )
        except NotFoundError:
            raise
        except Exception as e:
            raise ResumeGenerationError(
                f"Failed to generate cover letter for application '{application_id}': {e}"
            ) from e
