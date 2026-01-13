"""Tests for Bio model."""

from cveasy.models.bio import Bio


def test_bio_creation():
    """Test creating a bio with name only - location defaults to empty string."""
    bio = Bio(
        name="John Doe",
    )

    assert bio.name == "John Doe"
    assert bio.location == ""


def test_bio_creation_with_location():
    """Test creating a bio with name and location."""
    bio = Bio(
        name="John Doe",
        location="San Francisco, CA",
    )

    assert bio.name == "John Doe"
    assert bio.location == "San Francisco, CA"


def test_bio_to_frontmatter_dict():
    """Test converting bio to frontmatter dictionary."""
    bio = Bio(
        name="John Doe",
        location="San Francisco, CA",
    )

    data = bio.to_frontmatter_dict()
    assert data["name"] == "John Doe"
    assert data["location"] == "San Francisco, CA"
    assert "created" in data
    assert "updated" in data


def test_bio_to_frontmatter_dict_no_location():
    """Test converting bio to frontmatter dictionary - location always included as empty string."""
    bio = Bio(
        name="John Doe",
    )

    data = bio.to_frontmatter_dict()
    assert data["name"] == "John Doe"
    assert "location" in data
    assert data["location"] == ""


def test_bio_from_frontmatter_dict():
    """Test creating bio from frontmatter dictionary."""
    data = {
        "name": "John Doe",
        "location": "San Francisco, CA",
        "created": "2024-01-01T00:00:00",
        "updated": "2024-01-01T00:00:00",
    }

    bio = Bio.from_frontmatter_dict(data)
    assert bio.name == "John Doe"
    assert bio.location == "San Francisco, CA"
    assert bio.created is not None
    assert bio.updated is not None


def test_bio_from_frontmatter_dict_no_location():
    """Test creating bio from frontmatter dictionary without location - defaults to empty string."""
    data = {
        "name": "John Doe",
    }

    bio = Bio.from_frontmatter_dict(data)
    assert bio.name == "John Doe"
    assert bio.location == ""


def test_bio_location_defaults_to_empty_string():
    """Test that bio model always has location attribute defaulting to empty string."""
    # Test default initialization
    bio1 = Bio(name="John Doe")
    assert bio1.location == ""
    assert isinstance(bio1.location, str)

    # Test explicit empty string
    bio2 = Bio(name="Jane Doe", location="")
    assert bio2.location == ""

    # Test with actual location
    bio3 = Bio(name="Bob Smith", location="New York, NY")
    assert bio3.location == "New York, NY"

    # Test that to_frontmatter_dict always includes location
    data1 = bio1.to_frontmatter_dict()
    assert "location" in data1
    assert data1["location"] == ""

    data2 = bio2.to_frontmatter_dict()
    assert "location" in data2
    assert data2["location"] == ""

    data3 = bio3.to_frontmatter_dict()
    assert "location" in data3
    assert data3["location"] == "New York, NY"
