"""Markdown file I/O with frontmatter parsing."""

import frontmatter
from pathlib import Path
from typing import List, Optional, TypeVar, Generic
from slugify import slugify

from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.story import Story
from cveasy.models.link import Link
from cveasy.models.project import Project
from cveasy.models.job import Job
from cveasy.models.education import Education
from cveasy.models.bio import Bio
from cveasy.exceptions import StorageError

T = TypeVar("T", Skill, Experience, Story, Link, Project, Job, Education, Bio)


class MarkdownStorage(Generic[T]):
    """Storage for markdown files with frontmatter."""

    def __init__(self, base_path: Path):
        """
        Initialize storage with base path.

        Args:
            base_path: Base directory path for the project.
        """
        self.base_path = Path(base_path)

    def _get_directory(self, subdirectory: str) -> Path:
        """Get directory path, creating it if it doesn't exist."""
        path = self.base_path / subdirectory
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _slugify_name(self, name: str) -> str:
        """Convert name to slug for filename."""
        return slugify(name, lowercase=True)

    def save_skill(self, skill: Skill) -> Path:
        """Save skill to markdown file."""
        directory = self._get_directory("skills")
        filename = f"{self._slugify_name(skill.name)}.md"
        filepath = directory / filename

        post = frontmatter.Post(
            content=skill.content,
            **skill.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save skill to {filepath}: {e}") from e

        return filepath

    def load_skill(self, name: str) -> Optional[Skill]:
        """Load skill from markdown file."""
        directory = self._get_directory("skills")
        filename = f"{self._slugify_name(name)}.md"
        filepath = directory / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load skill from {filepath}: {e}") from e

        return Skill.from_frontmatter_dict(post.metadata, post.content)

    def list_skills(self) -> List[Skill]:
        """List all skills."""
        directory = self._get_directory("skills")
        skills = []

        for filepath in directory.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                skills.append(Skill.from_frontmatter_dict(post.metadata, post.content))
            except (IOError, OSError) as e:
                raise StorageError(f"Failed to load skill from {filepath}: {e}") from e

        return skills

    def save_experience(self, experience: Experience) -> Path:
        """Save experience to markdown file."""
        directory = self._get_directory("experiences")
        filename = f"{self._slugify_name(experience.title)}.md"
        filepath = directory / filename

        post = frontmatter.Post(
            content=experience.content,
            **experience.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save experience to {filepath}: {e}") from e

        return filepath

    def load_experience(self, title: str) -> Optional[Experience]:
        """Load experience from markdown file."""
        directory = self._get_directory("experiences")
        filename = f"{self._slugify_name(title)}.md"
        filepath = directory / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load experience from {filepath}: {e}") from e

        return Experience.from_frontmatter_dict(post.metadata, post.content)

    def list_experiences(self) -> List[Experience]:
        """List all experiences."""
        directory = self._get_directory("experiences")
        experiences = []

        for filepath in directory.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                experiences.append(Experience.from_frontmatter_dict(post.metadata, post.content))
            except (IOError, OSError) as e:
                raise StorageError(f"Failed to load experience from {filepath}: {e}") from e

        return experiences

    def save_story(self, story: Story) -> Path:
        """Save story to markdown file."""
        directory = self._get_directory("stories")
        filename = f"{self._slugify_name(story.title)}.md"
        filepath = directory / filename

        post = frontmatter.Post(
            content=story.content,
            **story.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save story to {filepath}: {e}") from e

        return filepath

    def load_story(self, title: str) -> Optional[Story]:
        """Load story from markdown file."""
        directory = self._get_directory("stories")
        filename = f"{self._slugify_name(title)}.md"
        filepath = directory / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load story from {filepath}: {e}") from e

        return Story.from_frontmatter_dict(post.metadata, post.content)

    def list_stories(self) -> List[Story]:
        """List all stories."""
        directory = self._get_directory("stories")
        stories = []

        for filepath in directory.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                stories.append(Story.from_frontmatter_dict(post.metadata, post.content))
            except (IOError, OSError) as e:
                raise StorageError(f"Failed to load story from {filepath}: {e}") from e

        return stories

    def save_link(self, link: Link) -> Path:
        """Save link to markdown file."""
        directory = self._get_directory("links")
        filename = f"{self._slugify_name(link.name)}.md"
        filepath = directory / filename

        post = frontmatter.Post(
            content="",
            **link.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save link to {filepath}: {e}") from e

        return filepath

    def load_link(self, name: str) -> Optional[Link]:
        """Load link from markdown file."""
        directory = self._get_directory("links")
        filename = f"{self._slugify_name(name)}.md"
        filepath = directory / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load link from {filepath}: {e}") from e

        return Link.from_frontmatter_dict(post.metadata, post.content)

    def list_links(self) -> List[Link]:
        """List all links."""
        directory = self._get_directory("links")
        links = []

        for filepath in directory.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                links.append(Link.from_frontmatter_dict(post.metadata, post.content))
            except (IOError, OSError) as e:
                raise StorageError(f"Failed to load link from {filepath}: {e}") from e

        return links

    def save_project(self, project: Project) -> Path:
        """Save project to markdown file."""
        directory = self._get_directory("projects")
        filename = f"{self._slugify_name(project.name)}.md"
        filepath = directory / filename

        post = frontmatter.Post(
            content=project.content,
            **project.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save project to {filepath}: {e}") from e

        return filepath

    def load_project(self, name: str) -> Optional[Project]:
        """Load project from markdown file."""
        directory = self._get_directory("projects")
        filename = f"{self._slugify_name(name)}.md"
        filepath = directory / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load project from {filepath}: {e}") from e

        return Project.from_frontmatter_dict(post.metadata, post.content)

    def list_projects(self) -> List[Project]:
        """List all projects."""
        directory = self._get_directory("projects")
        projects = []

        for filepath in directory.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                projects.append(Project.from_frontmatter_dict(post.metadata, post.content))
            except (IOError, OSError) as e:
                raise StorageError(f"Failed to load project from {filepath}: {e}") from e

        return projects

    def save_job(self, job: Job, application_id: str) -> Path:
        """Save job description to application directory."""
        directory = self._get_directory("applications") / application_id
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / "job-description.md"

        post = frontmatter.Post(
            content=job.content,
            **job.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save job to {filepath}: {e}") from e

        return filepath

    def load_job(self, application_id: str) -> Optional[Job]:
        """Load job description from application directory."""
        directory = self._get_directory("applications") / application_id
        filepath = directory / "job-description.md"

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load job from {filepath}: {e}") from e

        return Job.from_frontmatter_dict(post.metadata, post.content)

    def list_applications(self) -> List[str]:
        """List all application IDs (directory names)."""
        applications_dir = self._get_directory("applications")
        applications = []

        for item in applications_dir.iterdir():
            if item.is_dir() and (item / "job-description.md").exists():
                applications.append(item.name)

        return sorted(applications)

    def save_education(self, education: Education) -> Path:
        """Save education to markdown file."""
        directory = self._get_directory("education")
        filename = f"{self._slugify_name(education.name)}.md"
        filepath = directory / filename

        post = frontmatter.Post(
            content=education.content,
            **education.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save education to {filepath}: {e}") from e

        return filepath

    def load_education(self, name: str) -> Optional[Education]:
        """Load education from markdown file."""
        directory = self._get_directory("education")
        filename = f"{self._slugify_name(name)}.md"
        filepath = directory / filename

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load education from {filepath}: {e}") from e

        return Education.from_frontmatter_dict(post.metadata, post.content)

    def list_educations(self) -> List[Education]:
        """List all educations."""
        directory = self._get_directory("education")
        educations = []

        for filepath in directory.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                educations.append(Education.from_frontmatter_dict(post.metadata, post.content))
            except (IOError, OSError) as e:
                raise StorageError(f"Failed to load education from {filepath}: {e}") from e

        return educations

    def save_bio(self, bio: Bio) -> Path:
        """Save bio to markdown file at project root."""
        filepath = self.base_path / "bio.md"

        post = frontmatter.Post(
            content="",
            **bio.to_frontmatter_dict()
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save bio to {filepath}: {e}") from e

        return filepath

    def load_bio(self) -> Optional[Bio]:
        """Load bio from markdown file at project root."""
        filepath = self.base_path / "bio.md"

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load bio from {filepath}: {e}") from e

        return Bio.from_frontmatter_dict(post.metadata, post.content)

    def save_resume(self, content: str, application_id: Optional[str] = None) -> Path:
        """Save generated resume."""
        if application_id:
            directory = self._get_directory("applications") / application_id
            directory.mkdir(parents=True, exist_ok=True)
            filepath = directory / "resume.md"
        else:
            from datetime import datetime
            directory = self._get_directory("resume")
            date_str = datetime.now().strftime("%Y%m%d")
            filepath = directory / f"resume-{date_str}.md"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save resume to {filepath}: {e}") from e

        return filepath

    def load_resume(self, application_id: Optional[str] = None, date: Optional[str] = None) -> Optional[str]:
        """Load resume content."""
        if application_id:
            filepath = self.base_path / "applications" / application_id / "resume.md"
        elif date:
            filepath = self.base_path / "resume" / f"resume-{date}.md"
        else:
            # Load most recent general resume
            resume_dir = self.base_path / "resume"
            if not resume_dir.exists():
                return None
            resumes = sorted(resume_dir.glob("resume-*.md"), reverse=True)
            if not resumes:
                return None
            filepath = resumes[0]

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load resume from {filepath}: {e}") from e

    def save_check_report(self, content: str, application_id: str) -> Path:
        """Save check report to application directory."""
        directory = self._get_directory("applications") / application_id
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / "check-report.md"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save check report to {filepath}: {e}") from e

        return filepath

    def load_check_report(self, application_id: str) -> Optional[str]:
        """Load check report from application directory."""
        filepath = self.base_path / "applications" / application_id / "check-report.md"

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load check report from {filepath}: {e}") from e
