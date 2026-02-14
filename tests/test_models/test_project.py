"""Tests for Project model."""

import re
from cveasy.models.project import Project


def test_project_creation():
    """Test creating a project."""
    project = Project(
        name="E-commerce Platform",
        description="Full-stack application",
        link="https://github.com/user/proj",
    )

    assert project.name == "E-commerce Platform"
    assert project.description == "Full-stack application"
    assert project.link == "https://github.com/user/proj"
    # Verify slug is generated
    assert project.slug
    assert project.slug.startswith("e-commerce-platform-")
    assert len(project.slug.split("-")[-1]) == 6  # 6-char hash


def test_project_slug_format():
    """Test that slug has correct format."""
    project = Project(name="Task Management App", description="React app")

    # Slug should be lowercase, use hyphens, and have 6-char hash
    assert project.slug.islower()
    assert "-" in project.slug
    hash_part = project.slug.split("-")[-1]
    assert len(hash_part) == 6
    assert re.match(r"^[a-f0-9]{6}$", hash_part)


def test_project_frontmatter_serialization():
    """Test project frontmatter serialization."""
    project = Project(name="E-commerce Platform", description="Full-stack application")

    frontmatter_dict = project.to_frontmatter_dict()
    assert frontmatter_dict["name"] == "E-commerce Platform"
    assert frontmatter_dict["slug"] == project.slug


def test_project_related_experiences_field():
    """Test that related_experiences field works correctly."""
    project = Project(
        name="E-commerce Platform",
        description="Full-stack application",
        related_experiences=["software-engineer-abc123"],
    )

    assert project.related_experiences == ["software-engineer-abc123"]

    frontmatter = project.to_frontmatter_dict()
    assert frontmatter["related_experiences"] == ["software-engineer-abc123"]


def test_project_related_experiences_default_empty():
    """Test that related_experiences defaults to empty list."""
    project = Project(name="E-commerce Platform", description="Full-stack application")
    assert project.related_experiences == []

    frontmatter = project.to_frontmatter_dict()
    assert frontmatter["related_experiences"] == []


def test_project_from_frontmatter_with_related_experiences():
    """Test from_frontmatter_dict with related_experiences."""
    data = {
        "name": "E-commerce Platform",
        "description": "Full-stack application",
        "related_experiences": ["software-engineer-abc123"],
    }

    project = Project.from_frontmatter_dict(data)

    assert project.related_experiences == ["software-engineer-abc123"]
