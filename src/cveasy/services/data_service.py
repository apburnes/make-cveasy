"""Service for managing resume data (skills, experiences, stories, etc.)."""

from pathlib import Path
from typing import Optional, List

from cveasy.storage import MarkdownStorage
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.story import Story
from cveasy.models.link import Link
from cveasy.models.project import Project
from cveasy.models.education import Education
from cveasy.models.bio import Bio
from cveasy.exceptions import NotFoundError, ValidationError


class DataService:
    """Service for CRUD operations on resume data."""

    def __init__(self, project_path: Path):
        """
        Initialize data service.

        Args:
            project_path: Path to the project directory.
        """
        self.storage = MarkdownStorage(project_path)

    # Skills
    def create_skill(self, name: str) -> Path:
        """Create a new skill."""
        skill = Skill(
            name=name,
            category=None,
            years=None,
            proficiency=None,
            related_experience=[],
            content="",
        )
        return self.storage.save_skill(skill)

    def get_skill(self, name: str) -> Skill:
        """Get a skill by name."""
        skill = self.storage.load_skill(name)
        if not skill:
            raise NotFoundError(f"Skill '{name}' not found.")
        return skill

    def list_skills(self) -> List[Skill]:
        """List all skills."""
        return self.storage.list_skills()

    # Experiences
    def create_experience(self, title: str) -> Path:
        """Create a new experience."""
        experience = Experience(
            title=title,
            organization="",
            start_date=None,
            end_date=None,
            location=None,
            related_skills=[],
            related_stories=[],
            content="",
        )
        return self.storage.save_experience(experience)

    def get_experience(self, title: str) -> Experience:
        """Get an experience by title."""
        experience = self.storage.load_experience(title)
        if not experience:
            raise NotFoundError(f"Experience '{title}' not found.")
        return experience

    def list_experiences(self) -> List[Experience]:
        """List all experiences."""
        return self.storage.list_experiences()

    # Stories
    def create_story(self, title: str) -> Path:
        """Create a new story."""
        story = Story(
            title=title,
            context=None,
            outcome=None,
            content="",
        )
        return self.storage.save_story(story)

    def get_story(self, title: str) -> Story:
        """Get a story by title."""
        story = self.storage.load_story(title)
        if not story:
            raise NotFoundError(f"Story '{title}' not found.")
        return story

    def list_stories(self) -> List[Story]:
        """List all stories."""
        return self.storage.list_stories()

    # Links
    def create_link(self, name: str, description: str, url: str) -> Path:
        """Create a new link."""
        if not url or not url.startswith(("http://", "https://")):
            raise ValidationError(f"Invalid URL: {url}. Must start with http:// or https://")
        link = Link(name=name, description=description, url=url)
        return self.storage.save_link(link)

    def get_link(self, name: str) -> Link:
        """Get a link by name."""
        link = self.storage.load_link(name)
        if not link:
            raise NotFoundError(f"Link '{name}' not found.")
        return link

    def list_links(self) -> List[Link]:
        """List all links."""
        return self.storage.list_links()

    # Projects
    def create_project(self, name: str, description: str, link: Optional[str] = None) -> Path:
        """Create a new project."""
        if link and not link.startswith(("http://", "https://")):
            raise ValidationError(f"Invalid URL: {link}. Must start with http:// or https://")
        project = Project(name=name, description=description, link=link, content="")
        return self.storage.save_project(project)

    def get_project(self, name: str) -> Project:
        """Get a project by name."""
        project = self.storage.load_project(name)
        if not project:
            raise NotFoundError(f"Project '{name}' not found.")
        return project

    def list_projects(self) -> List[Project]:
        """List all projects."""
        return self.storage.list_projects()

    # Education
    def create_education(
        self,
        name: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        degree: Optional[str] = None,
        certificate: Optional[str] = None,
        organization: Optional[str] = None,
    ) -> Path:
        """Create a new education entry."""
        education = Education(
            name=name,
            start_date=start_date,
            end_date=end_date,
            degree=degree,
            certificate=certificate,
            organization=organization,
            content="",
        )
        return self.storage.save_education(education)

    def get_education(self, name: str) -> Education:
        """Get an education entry by name."""
        education = self.storage.load_education(name)
        if not education:
            raise NotFoundError(f"Education '{name}' not found.")
        return education

    def list_educations(self) -> List[Education]:
        """List all education entries."""
        return self.storage.list_educations()

    # Bio
    def create_or_update_bio(self, name: str, location: Optional[str] = None) -> Path:
        """Create or update bio information."""
        bio = Bio(name=name, location=location or "")
        return self.storage.save_bio(bio)

    def get_bio(self) -> Optional[Bio]:
        """Get bio information."""
        return self.storage.load_bio()
