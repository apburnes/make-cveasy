"""Tests for Story model."""

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
