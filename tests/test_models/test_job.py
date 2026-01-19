"""Tests for Job model."""

import re
from cveasy.models.job import Job


def test_job_creation():
    """Test creating a job."""
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
    )

    assert job.name == "Software Engineer"
    assert job.title == "Senior Software Engineer"
    assert job.location == "Remote"
    assert job.requirements == "Python, AWS"
    # Verify slug is generated
    assert job.slug
    assert job.slug.startswith("software-engineer-")
    assert len(job.slug.split("-")[-1]) == 6  # 6-char hash


def test_job_slug_format():
    """Test that slug has correct format."""
    job = Job(name="Senior Software Engineer Position")

    # Slug should be lowercase, use hyphens, and have 6-char hash
    assert job.slug.islower()
    assert "-" in job.slug
    hash_part = job.slug.split("-")[-1]
    assert len(hash_part) == 6
    assert re.match(r"^[a-f0-9]{6}$", hash_part)


def test_job_frontmatter_serialization():
    """Test job frontmatter serialization."""
    job = Job(name="Software Engineer", title="Senior Software Engineer")

    frontmatter_dict = job.to_frontmatter_dict()
    assert frontmatter_dict["name"] == "Software Engineer"
    assert frontmatter_dict["slug"] == job.slug
