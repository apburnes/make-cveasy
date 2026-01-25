"""Service for checking resume quality against job descriptions."""

from pathlib import Path

from cveasy.storage import MarkdownStorage
from cveasy.analysis import ResumeChecker
from cveasy.analysis.matcher import validate_spacy_model
from cveasy.exceptions import NotFoundError


class CheckService:
    """Service for checking resume quality."""

    def __init__(self, project_path: Path):
        """
        Initialize check service.

        Args:
            project_path: Path to the project directory.
        """
        self.storage = MarkdownStorage(project_path)
        self.checker = ResumeChecker()
        self.project_path = project_path

    def check_resume(self, application_id: str) -> tuple[str, Path]:
        """
        Check resume quality against job description.

        Args:
            application_id: ID of the job application.

        Returns:
            Tuple of (check_report_content, report_filepath).

        Raises:
            NotFoundError: If application not found.
            ValidationError: If spaCy model is not available.
        """
        # Validate spaCy model is available before proceeding
        validate_spacy_model("en_core_web_sm")

        # Check if resume exists, generate if not
        resume_content = self.storage.load_resume(application_id=application_id)

        if not resume_content:
            # Generate resume first
            from cveasy.services.resume_service import ResumeService
            resume_service = ResumeService(self.project_path)
            resume_service.generate_customized_resume(application_id)
            resume_content = self.storage.load_resume(application_id=application_id)
            if not resume_content:
                raise NotFoundError(
                    f"Failed to generate resume for application '{application_id}'"
                )

        # Load job description
        job = self.storage.load_job(application_id)
        if not job:
            raise NotFoundError(
                f"Job application '{application_id}' not found. "
                f"Create it first with: cveasy add job --name <name>"
            )

        # Load skills for matching
        skills = self.storage.list_skills()

        # Run check
        report = self.checker.check(resume_content, job, skills)

        # Save report
        filepath = self.storage.save_check_report(report, application_id)

        return report, filepath
