"""Tests for Link model."""

from cveasy.models.link import Link


def test_link_creation():
    """Test creating a link."""
    link = Link(
        name="LinkedIn",
        description="Professional profile",
        url="https://linkedin.com/in/user",
    )

    assert link.name == "LinkedIn"
    assert link.description == "Professional profile"
    assert link.url == "https://linkedin.com/in/user"
