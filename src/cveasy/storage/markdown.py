"""Markdown file I/O with frontmatter parsing."""

import logging
import re

import frontmatter
from pathlib import Path
from typing import Dict, List, Optional, Type, TypeVar, Generic
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

logger = logging.getLogger(__name__)

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
        self._cache: dict[str, list] = {}

    def _get_directory(self, subdirectory: str) -> Path:
        """Get directory path, creating it if it doesn't exist."""
        path = self.base_path / subdirectory
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _slugify_name(self, name: str) -> str:
        """Convert name to slug for filename."""
        return slugify(name, lowercase=True)

    def _save_entity(self, entity, subdirectory: str, entity_type_name: str) -> Path:
        """Save an entity to a markdown file."""
        directory = self._get_directory(subdirectory)
        filename = f"{entity.slug}.md"
        filepath = directory / filename

        post = frontmatter.Post(
            content=getattr(entity, "content", ""),
            **entity.to_frontmatter_dict(),
        )

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(frontmatter.dumps(post))
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save {entity_type_name} to {filepath}: {e}") from e

        self._cache.pop(subdirectory, None)
        logger.debug(
            "Saved %s to %s (cache invalidated for '%s')", entity_type_name, filepath, subdirectory
        )
        return filepath

    def _load_entity(
        self,
        name: str,
        subdirectory: str,
        model_class: Type[T],
        name_field: str,
        entity_type_name: str,
    ) -> Optional[T]:
        """Load an entity from a markdown file by name/title."""
        directory = self._get_directory(subdirectory)

        slug_filename = f"{self._slugify_name(name)}.md"
        filepath = directory / slug_filename

        # If file doesn't exist with slug-based name, search all files
        if not filepath.exists():
            for filepath in directory.glob("*.md"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        post = frontmatter.load(f)
                    if post.metadata.get(name_field) == name:
                        return model_class.from_frontmatter_dict(post.metadata, post.content)
                except (IOError, OSError):
                    continue
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                post = frontmatter.load(f)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load {entity_type_name} from {filepath}: {e}") from e

        entity = model_class.from_frontmatter_dict(post.metadata, post.content)
        # Verify name matches (for backward compatibility)
        if getattr(entity, name_field) != name:
            for filepath in directory.glob("*.md"):
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        post = frontmatter.load(f)
                    if post.metadata.get(name_field) == name:
                        return model_class.from_frontmatter_dict(post.metadata, post.content)
                except (IOError, OSError):
                    continue
            return None

        return entity

    def _list_entities(
        self, subdirectory: str, model_class: Type[T], entity_type_name: str
    ) -> List[T]:
        """List all entities of a given type. Results are cached until a write invalidates."""
        if subdirectory in self._cache:
            logger.debug(
                "Cache hit for '%s' (%d entities)", subdirectory, len(self._cache[subdirectory])
            )
            return list(self._cache[subdirectory])

        directory = self._get_directory(subdirectory)
        entities = []

        for filepath in directory.glob("*.md"):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    post = frontmatter.load(f)
                entities.append(model_class.from_frontmatter_dict(post.metadata, post.content))
            except (IOError, OSError) as e:
                raise StorageError(f"Failed to load {entity_type_name} from {filepath}: {e}") from e

        self._cache[subdirectory] = entities
        logger.debug("Loaded %d %s(s) from disk", len(entities), entity_type_name)
        return list(entities)

    def save_skill(self, skill: Skill) -> Path:
        """Save skill to markdown file."""
        return self._save_entity(skill, "skills", "skill")

    def load_skill(self, name: str) -> Optional[Skill]:
        """Load skill from markdown file."""
        return self._load_entity(name, "skills", Skill, "name", "skill")

    def list_skills(self) -> List[Skill]:
        """List all skills."""
        return self._list_entities("skills", Skill, "skill")

    def save_experience(self, experience: Experience) -> Path:
        """Save experience to markdown file."""
        return self._save_entity(experience, "experiences", "experience")

    def load_experience(self, title: str) -> Optional[Experience]:
        """Load experience from markdown file."""
        return self._load_entity(title, "experiences", Experience, "title", "experience")

    def list_experiences(self) -> List[Experience]:
        """List all experiences."""
        return self._list_entities("experiences", Experience, "experience")

    def save_story(self, story: Story) -> Path:
        """Save story to markdown file."""
        return self._save_entity(story, "stories", "story")

    def load_story(self, title: str) -> Optional[Story]:
        """Load story from markdown file."""
        return self._load_entity(title, "stories", Story, "title", "story")

    def list_stories(self) -> List[Story]:
        """List all stories."""
        return self._list_entities("stories", Story, "story")

    def save_link(self, link: Link) -> Path:
        """Save link to markdown file."""
        return self._save_entity(link, "links", "link")

    def load_link(self, name: str) -> Optional[Link]:
        """Load link from markdown file."""
        return self._load_entity(name, "links", Link, "name", "link")

    def list_links(self) -> List[Link]:
        """List all links."""
        return self._list_entities("links", Link, "link")

    def save_project(self, project: Project) -> Path:
        """Save project to markdown file."""
        return self._save_entity(project, "projects", "project")

    def load_project(self, name: str) -> Optional[Project]:
        """Load project from markdown file."""
        return self._load_entity(name, "projects", Project, "name", "project")

    def list_projects(self) -> List[Project]:
        """List all projects."""
        return self._list_entities("projects", Project, "project")

    def save_job(self, job: Job, application_id: str) -> Path:
        """Save job description to application directory."""
        directory = self._get_directory("applications") / application_id
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / "job-description.md"

        post = frontmatter.Post(content=job.content, **job.to_frontmatter_dict())

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
        return self._save_entity(education, "education", "education")

    def load_education(self, name: str) -> Optional[Education]:
        """Load education from markdown file."""
        return self._load_entity(name, "education", Education, "name", "education")

    def list_educations(self) -> List[Education]:
        """List all educations."""
        return self._list_entities("education", Education, "education")

    def load_all_candidate_data(self) -> Dict:
        """Load all candidate data (bio, skills, experiences, stories, links, projects, educations)."""
        return {
            "bio": self.load_bio(),
            "skills": self.list_skills(),
            "experiences": self.list_experiences(),
            "stories": self.list_stories(),
            "links": self.list_links(),
            "projects": self.list_projects(),
            "educations": self.list_educations(),
        }

    def _validate_markdown_content(self, content: str, content_type: str) -> str:
        """Validate and clean LLM-generated markdown content before saving."""
        content = content.strip()
        if not content:
            raise StorageError(f"Generated {content_type} is empty")
        if len(content) < 50:
            raise StorageError(
                f"Generated {content_type} is suspiciously short ({len(content)} chars)"
            )
        if content.startswith("```"):
            content = re.sub(r"^```\w*\n?", "", content)
            content = re.sub(r"\n?```$", "", content)
            content = content.strip()
        return content

    def save_bio(self, bio: Bio) -> Path:
        """Save bio to markdown file at project root."""
        filepath = self.base_path / "bio.md"

        post = frontmatter.Post(content="", **bio.to_frontmatter_dict())

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
        content = self._validate_markdown_content(content, "resume")
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

    def load_resume(
        self, application_id: Optional[str] = None, date: Optional[str] = None
    ) -> Optional[str]:
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
        content = self._validate_markdown_content(content, "check report")
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

    def save_cover_letter(self, content: str, application_id: str) -> Path:
        """Save cover letter to application directory."""
        content = self._validate_markdown_content(content, "cover letter")
        directory = self._get_directory("applications") / application_id
        directory.mkdir(parents=True, exist_ok=True)
        filepath = directory / "cover-letter.md"

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to save cover letter to {filepath}: {e}") from e

        return filepath

    def load_cover_letter(self, application_id: str) -> Optional[str]:
        """Load cover letter from application directory."""
        filepath = self.base_path / "applications" / application_id / "cover-letter.md"

        if not filepath.exists():
            return None

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except (IOError, OSError) as e:
            raise StorageError(f"Failed to load cover letter from {filepath}: {e}") from e
