"""Tests for Project model."""

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
