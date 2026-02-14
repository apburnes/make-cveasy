"""Tests for Story model."""

import re
from cveasy.models.story import Story


def test_story_creation():
    """Test creating a story."""
    story = Story(
        title="Led Migration",
        context="Company needed to scale",
        outcome="Reduced time by 50%",
    )

    assert story.title == "Led Migration"
    assert story.context == "Company needed to scale"
    assert story.outcome == "Reduced time by 50%"
    # Verify slug is generated
    assert story.slug
    assert story.slug.startswith("led-migration-")
    assert len(story.slug.split("-")[-1]) == 6  # 6-char hash


def test_story_slug_format():
    """Test that slug has correct format."""
    story = Story(title="Led Migration to Microservices")

    # Slug should be lowercase, use hyphens, and have 6-char hash
    assert story.slug.islower()
    assert "-" in story.slug
    hash_part = story.slug.split("-")[-1]
    assert len(hash_part) == 6
    assert re.match(r"^[a-f0-9]{6}$", hash_part)


def test_story_frontmatter_serialization():
    """Test story frontmatter serialization."""
    story = Story(title="Led Migration")

    frontmatter_dict = story.to_frontmatter_dict()
    assert frontmatter_dict["title"] == "Led Migration"
    assert frontmatter_dict["slug"] == story.slug


def test_story_related_experiences_field():
    """Test that related_experiences field works correctly."""
    story = Story(
        title="Led Migration",
        related_experiences=["software-engineer-abc123"],
    )

    assert story.related_experiences == ["software-engineer-abc123"]

    frontmatter = story.to_frontmatter_dict()
    assert frontmatter["related_experiences"] == ["software-engineer-abc123"]


def test_story_related_experiences_default_empty():
    """Test that related_experiences defaults to empty list."""
    story = Story(title="Led Migration")
    assert story.related_experiences == []

    frontmatter = story.to_frontmatter_dict()
    assert frontmatter["related_experiences"] == []


def test_story_from_frontmatter_with_related_experiences():
    """Test from_frontmatter_dict with related_experiences."""
    data = {
        "title": "Led Migration",
        "related_experiences": ["software-engineer-abc123"],
    }

    story = Story.from_frontmatter_dict(data)

    assert story.related_experiences == ["software-engineer-abc123"]
