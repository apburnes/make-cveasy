"""Tests for Skill model."""

import re
from cveasy.models.skill import Skill


def test_skill_creation():
    """Test creating a skill."""
    skill = Skill(
        name="Python",
        category="Programming Language",
        years=5,
        proficiency="Expert",
    )

    assert skill.name == "Python"
    assert skill.category == "Programming Language"
    assert skill.years == 5
    assert skill.proficiency == "Expert"
    # Verify slug is generated
    assert skill.slug
    assert skill.slug.startswith("python-")
    assert len(skill.slug.split("-")[-1]) == 6  # 6-char hash


def test_skill_frontmatter_serialization():
    """Test skill frontmatter serialization."""
    skill = Skill(
        name="Python",
        category="Programming Language",
        years=5,
        proficiency="Expert",
        content="Test content",
    )

    frontmatter_dict = skill.to_frontmatter_dict()

    assert frontmatter_dict["name"] == "Python"
    assert frontmatter_dict["slug"] == skill.slug
    assert frontmatter_dict["category"] == "Programming Language"
    assert frontmatter_dict["years"] == 5
    assert frontmatter_dict["proficiency"] == "Expert"


def test_skill_from_frontmatter():
    """Test creating skill from frontmatter."""
    data = {
        "name": "Python",
        "category": "Programming Language",
        "years": 5,
        "proficiency": "Expert",
    }

    skill = Skill.from_frontmatter_dict(data, content="Test content")

    assert skill.name == "Python"
    assert skill.category == "Programming Language"
    assert skill.years == 5
    assert skill.proficiency == "Expert"
    assert skill.content == "Test content"
    # Slug should be generated if not present
    assert skill.slug
    assert skill.slug.startswith("python-")


def test_skill_slug_format():
    """Test that slug has correct format."""
    skill = Skill(name="Python Programming")

    # Slug should be lowercase, use hyphens, and have 6-char hash
    assert skill.slug.islower()
    assert "-" in skill.slug
    # Extract hash (last 6 chars after last hyphen)
    hash_part = skill.slug.split("-")[-1]
    assert len(hash_part) == 6
    assert re.match(r"^[a-f0-9]{6}$", hash_part)  # Hex characters


def test_skill_slug_from_frontmatter():
    """Test loading skill with existing slug in frontmatter."""
    data = {
        "name": "Python",
        "slug": "python-abc123",
        "category": "Programming Language",
    }

    skill = Skill.from_frontmatter_dict(data)

    assert skill.slug == "python-abc123"
    assert skill.name == "Python"


def test_skill_related_experiences_field():
    """Test that related_experiences field works correctly."""
    skill = Skill(
        name="Python",
        related_experiences=["software-engineer-abc123"],
    )

    assert skill.related_experiences == ["software-engineer-abc123"]

    frontmatter = skill.to_frontmatter_dict()
    assert frontmatter["related_experiences"] == ["software-engineer-abc123"]


def test_skill_from_frontmatter_backward_compat():
    """Test from_frontmatter_dict with old related_experience key."""
    data = {
        "name": "Python",
        "related_experience": ["software-engineer-abc123"],
    }

    skill = Skill.from_frontmatter_dict(data)

    assert skill.related_experiences == ["software-engineer-abc123"]


def test_skill_from_frontmatter_new_key():
    """Test from_frontmatter_dict with new related_experiences key."""
    data = {
        "name": "Python",
        "related_experiences": ["software-engineer-abc123"],
    }

    skill = Skill.from_frontmatter_dict(data)

    assert skill.related_experiences == ["software-engineer-abc123"]
