"""Tests for Experience model."""

import re
from cveasy.models.experience import Experience


def test_experience_creation():
    """Test creating an experience."""
    exp = Experience(
        title="Software Engineer",
        organization="Tech Corp",
        start_date="2020-01",
        end_date="2024-01",
    )

    assert exp.title == "Software Engineer"
    assert exp.organization == "Tech Corp"
    assert exp.start_date == "2020-01"
    assert exp.end_date == "2024-01"
    # Verify slug is generated
    assert exp.slug
    assert exp.slug.startswith("software-engineer-")
    assert len(exp.slug.split("-")[-1]) == 6  # 6-char hash


def test_experience_frontmatter_serialization():
    """Test experience frontmatter serialization."""
    exp = Experience(
        title="Software Engineer",
        organization="Tech Corp",
        start_date="2020-01",
        end_date="2024-01",
        location="San Francisco",
    )

    frontmatter_dict = exp.to_frontmatter_dict()

    assert frontmatter_dict["title"] == "Software Engineer"
    assert frontmatter_dict["slug"] == exp.slug
    assert frontmatter_dict["organization"] == "Tech Corp"
    assert frontmatter_dict["start_date"] == "2020-01"
    assert frontmatter_dict["location"] == "San Francisco"


def test_experience_slug_format():
    """Test that slug has correct format."""
    exp = Experience(title="Senior Software Engineer", organization="Tech Corp")

    # Slug should be lowercase, use hyphens, and have 6-char hash
    assert exp.slug.islower()
    assert "-" in exp.slug
    # Extract hash (last 6 chars after last hyphen)
    hash_part = exp.slug.split("-")[-1]
    assert len(hash_part) == 6
    assert re.match(r"^[a-f0-9]{6}$", hash_part)  # Hex characters


def test_experience_date_validator_truncates_yyyy_mm_dd():
    """Test that YYYY-MM-DD dates are truncated to YYYY-MM."""
    exp = Experience(
        title="Engineer",
        organization="Corp",
        start_date="2020-01-15",
        end_date="2024-06-30",
    )
    assert exp.start_date == "2020-01"
    assert exp.end_date == "2024-06"


def test_experience_date_validator_passes_yyyy_mm():
    """Test that YYYY-MM dates pass through unchanged."""
    exp = Experience(
        title="Engineer",
        organization="Corp",
        start_date="2020-01",
        end_date="2024-06",
    )
    assert exp.start_date == "2020-01"
    assert exp.end_date == "2024-06"


def test_experience_date_validator_passes_yyyy():
    """Test that YYYY dates pass through."""
    exp = Experience(
        title="Engineer",
        organization="Corp",
        start_date="2020",
    )
    assert exp.start_date == "2020"


def test_experience_date_validator_normalizes_present():
    """Test that 'present' (any case) is normalized to 'Present'."""
    exp1 = Experience(title="Engineer", organization="Corp", end_date="present")
    assert exp1.end_date == "Present"

    exp2 = Experience(title="Engineer", organization="Corp", end_date="PRESENT")
    assert exp2.end_date == "Present"

    exp3 = Experience(title="Engineer", organization="Corp", end_date="Present")
    assert exp3.end_date == "Present"


def test_experience_date_validator_none_passes():
    """Test that None dates pass through."""
    exp = Experience(
        title="Engineer",
        organization="Corp",
        start_date=None,
        end_date=None,
    )
    assert exp.start_date is None
    assert exp.end_date is None
