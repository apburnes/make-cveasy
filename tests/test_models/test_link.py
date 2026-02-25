"""Tests for Link model."""

import re
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
    # Verify slug is generated
    assert link.slug
    assert link.slug.startswith("linkedin-")
    assert len(link.slug.split("-")[-1]) == 6  # 6-char hash


def test_link_slug_format():
    """Test that slug has correct format."""
    link = Link(name="GitHub Profile", description="Code repository", url="https://github.com/user")

    # Slug should be lowercase, use hyphens, and have 6-char hash
    assert link.slug.islower()
    assert "-" in link.slug
    hash_part = link.slug.split("-")[-1]
    assert len(hash_part) == 6
    assert re.match(r"^[a-f0-9]{6}$", hash_part)


def test_link_frontmatter_serialization():
    """Test link frontmatter serialization."""
    link = Link(
        name="LinkedIn", description="Professional profile", url="https://linkedin.com/in/user"
    )

    frontmatter_dict = link.to_frontmatter_dict()
    assert frontmatter_dict["name"] == "LinkedIn"
    assert frontmatter_dict["slug"] == link.slug


def test_link_url_validator_strips_whitespace():
    """Test URL validator strips whitespace."""
    link = Link(name="LinkedIn", description="Profile", url="  https://linkedin.com/in/user  ")
    assert link.url == "https://linkedin.com/in/user"


def test_link_url_validator_passes_normal_url():
    """Test URL validator passes through normal URLs."""
    link = Link(name="GitHub", description="Code", url="https://github.com/user")
    assert link.url == "https://github.com/user"
