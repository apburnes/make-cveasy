"""Service for resume generation and management."""

from pathlib import Path
from typing import Optional

from cveasy.storage import MarkdownStorage
from cveasy.ai import ResumeGenerator
from cveasy.exceptions import NotFoundError, ResumeGenerationError


class ResumeService:
    """Service for managing resume generation and updates."""

    def __init__(self, project_path: Path):
        """
        Initialize resume service.

        Args:
            project_path: Path to the project directory.
        """
        self.storage = MarkdownStorage(project_path)
        self.generator = ResumeGenerator()

    def generate_general_resume(self) -> Path:
        """
        Generate a general resume from all available data.

        Returns:
            Path to the saved resume file.

        Raises:
            ResumeGenerationError: If generation fails.
        """
        try:
            bio = self.storage.load_bio()
            skills = self.storage.list_skills()
            experiences = self.storage.list_experiences()
            stories = self.storage.list_stories()
            links = self.storage.list_links()
            projects = self.storage.list_projects()
            educations = self.storage.list_educations()

            resume_content = self.generator.generate_general_resume(
                skills=skills,
                experiences=experiences,
                stories=stories,
                links=links,
                projects=projects,
                educations=educations,
                bio=bio,
            )

            return self.storage.save_resume(resume_content)
        except Exception as e:
            raise ResumeGenerationError(f"Failed to generate general resume: {e}") from e

    def generate_customized_resume(self, application_id: str) -> Path:
        """
        Generate a customized resume for a specific job application.

        Args:
            application_id: ID of the job application.

        Returns:
            Path to the saved resume file.

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

            resume_content = self.generator.generate_customized_resume(
                job=job,
                skills=skills,
                experiences=experiences,
                stories=stories,
                links=links,
                projects=projects,
                educations=educations,
                bio=bio,
            )

            return self.storage.save_resume(resume_content, application_id=application_id)
        except NotFoundError:
            raise
        except Exception as e:
            raise ResumeGenerationError(
                f"Failed to generate customized resume for application '{application_id}': {e}"
            ) from e

    def update_resume_from_check_report(self, application_id: str) -> Path:
        """
        Update resume based on check report suggestions.

        Args:
            application_id: ID of the job application.

        Returns:
            Path to the saved resume file.

        Raises:
            NotFoundError: If application, resume, or check report not found.
            ResumeGenerationError: If update fails.
        """
        job = self.storage.load_job(application_id)
        if not job:
            raise NotFoundError(
                f"Job application '{application_id}' not found. "
                f"Create it first with: cveasy add job --name <name>"
            )

        current_resume = self.storage.load_resume(application_id=application_id)
        if not current_resume:
            raise NotFoundError(
                f"No resume found for application '{application_id}'. "
                f"Generate it first with: cveasy generate --application {application_id}"
            )

        check_report = self.storage.load_check_report(application_id)
        if not check_report:
            raise NotFoundError(
                f"No check report found for application '{application_id}'. "
                f"Run 'cveasy check --application {application_id}' first."
            )

        try:
            bio = self.storage.load_bio()
            skills = self.storage.list_skills()
            experiences = self.storage.list_experiences()
            stories = self.storage.list_stories()
            links = self.storage.list_links()
            projects = self.storage.list_projects()
            educations = self.storage.list_educations()

            resume_content = self.generator.update_resume_from_check_report(
                current_resume=current_resume,
                check_report=check_report,
                job=job,
                skills=skills,
                experiences=experiences,
                stories=stories,
                links=links,
                projects=projects,
                educations=educations,
                bio=bio,
            )

            return self.storage.save_resume(resume_content, application_id=application_id)
        except NotFoundError:
            raise
        except Exception as e:
            raise ResumeGenerationError(
                f"Failed to update resume for application '{application_id}': {e}"
            ) from e

    def get_resume(
        self, application_id: Optional[str] = None, date: Optional[str] = None
    ) -> Optional[str]:
        """
        Load resume content.

        Args:
            application_id: Optional application ID.
            date: Optional date string for general resumes.

        Returns:
            Resume content or None if not found.
        """
        return self.storage.load_resume(application_id=application_id, date=date)
