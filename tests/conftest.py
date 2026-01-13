"""Pytest configuration and fixtures."""

import pytest
from pathlib import Path
import tempfile
import shutil

from cveasy.storage import MarkdownStorage


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def storage(temp_dir):
    """Create a MarkdownStorage instance with temporary directory."""
    # Create subdirectories
    for subdir in ["skills", "experiences", "stories", "links", "projects", "applications", "resume"]:
        (temp_dir / subdir).mkdir(exist_ok=True)

    return MarkdownStorage(temp_dir)


@pytest.fixture
def sample_skill():
    """Sample skill for testing."""
    from cveasy.models.skill import Skill
    return Skill(
        name="Python",
        category="Programming Language",
        years=5,
        proficiency="Expert",
        related_experience=[],
        content="Extensive experience with Python development",
    )


@pytest.fixture
def sample_experience():
    """Sample experience for testing."""
    from cveasy.models.experience import Experience
    return Experience(
        title="Senior Software Engineer",
        organization="Tech Corp",
        start_date="2020-01-01",
        end_date="2024-01-01",
        location="San Francisco, CA",
        related_skills=[],
        related_stories=[],
        content="Led development of key features",
    )


@pytest.fixture
def sample_story():
    """Sample story for testing."""
    from cveasy.models.story import Story
    return Story(
        title="Led Migration to Microservices",
        context="Company needed to scale infrastructure",
        outcome="Reduced deployment time by 50%",
        content="Detailed description of the migration process",
    )


@pytest.fixture
def sample_link():
    """Sample link for testing."""
    from cveasy.models.link import Link
    return Link(
        name="LinkedIn",
        description="Professional profile",
        url="https://linkedin.com/in/username",
    )


@pytest.fixture
def sample_project():
    """Sample project for testing."""
    from cveasy.models.project import Project
    return Project(
        name="E-commerce Platform",
        description="Full-stack web application",
        link="https://github.com/user/project",
        content="Built using React and Node.js",
    )


@pytest.fixture
def sample_job():
    """Sample job for testing."""
    from cveasy.models.job import Job
    return Job(
        name="Software Engineer Position",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS, Docker",
        pay="$150k-200k",
        content="Full job description text here",
    )
