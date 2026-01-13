"""Tests for Job model."""

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
