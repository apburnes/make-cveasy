"""Tests for Experience model."""

from cveasy.models.experience import Experience


def test_experience_creation():
    """Test creating an experience."""
    exp = Experience(
        title="Software Engineer",
        organization="Tech Corp",
        start_date="2020-01-01",
        end_date="2024-01-01",
    )

    assert exp.title == "Software Engineer"
    assert exp.organization == "Tech Corp"
    assert exp.start_date == "2020-01-01"
    assert exp.end_date == "2024-01-01"


def test_experience_frontmatter_serialization():
    """Test experience frontmatter serialization."""
    exp = Experience(
        title="Software Engineer",
        organization="Tech Corp",
        start_date="2020-01-01",
        end_date="2024-01-01",
        location="San Francisco",
    )

    frontmatter_dict = exp.to_frontmatter_dict()

    assert frontmatter_dict["title"] == "Software Engineer"
    assert frontmatter_dict["organization"] == "Tech Corp"
    assert frontmatter_dict["start_date"] == "2020-01-01"
    assert frontmatter_dict["location"] == "San Francisco"
