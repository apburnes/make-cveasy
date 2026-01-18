"""Service for job application management."""

from pathlib import Path
from datetime import datetime
from typing import Optional, List
from slugify import slugify

from cveasy.storage import MarkdownStorage
from cveasy.scraping import JobScraper
from cveasy.models.job import Job
from cveasy.exceptions import NotFoundError, ImportError


class ApplicationService:
    """Service for managing job applications."""

    def __init__(self, project_path: Path):
        """
        Initialize application service.

        Args:
            project_path: Path to the project directory.
        """
        self.storage = MarkdownStorage(project_path)
        self.scraper = JobScraper()

    def create_application(self, name: str, url: Optional[str] = None) -> tuple[str, Path]:
        """
        Create a new job application.

        Args:
            name: Name of the job application.
            url: Optional URL to scrape job description from.

        Returns:
            Tuple of (application_id, filepath).

        Raises:
            ImportError: If scraping fails.
        """
        # Create application ID with date
        date_str = datetime.now().strftime("%Y%m%d")
        slugified_name = slugify(name, lowercase=True)
        application_id = f"{slugified_name}-{date_str}"

        if url:
            # Scrape job description
            try:
                job = self.scraper.scrape(url)
            except ImportError:
                # Scraping failed, create empty job
                job = None
            if not job:
                # Create empty job entry if scraping failed
                job = Job(
                    name=name,
                    title=None,
                    location=None,
                    requirements=None,
                    pay=None,
                    content="",
                )
            else:
                # Update name if not set
                if not job.name or job.name == "Job Application":
                    job.name = name
        else:
            # Create empty job entry
            job = Job(
                name=name,
                title=None,
                location=None,
                requirements=None,
                pay=None,
                content="",
            )

        filepath = self.storage.save_job(job, application_id)
        return application_id, filepath

    def get_application(self, application_id: str) -> Job:
        """
        Load a job application.

        Args:
            application_id: ID of the application.

        Returns:
            Job model.

        Raises:
            NotFoundError: If application not found.
        """
        job = self.storage.load_job(application_id)
        if not job:
            raise NotFoundError(
                f"Job application '{application_id}' not found. "
                f"Create it first with: cveasy add job --name <name>"
            )
        return job

    def list_applications(self) -> List[str]:
        """
        List all application IDs.

        Returns:
            List of application IDs.
        """
        return self.storage.list_applications()

    def scrape_job_description(self, url: str) -> Job:
        """
        Scrape job description from URL.

        Args:
            url: URL to scrape.

        Returns:
            Job model with scraped data.

        Raises:
            ImportError: If scraping fails.
        """
        job = self.scraper.scrape(url)
        if not job:
            raise ImportError(
                f"Could not scrape job description from {url}. "
                f"Please check the URL and try again."
            )
        return job
