"""Tests for Skill model."""

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
