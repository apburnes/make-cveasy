"""Tests for Education model."""

from cveasy.models.education import Education


def test_education_creation():
    """Test creating an education."""
    edu = Education(
        name="Bachelor of Science in Computer Science",
        organization="University Name",
        degree="Bachelor of Science",
        start_date="2018-09",
        end_date="2022-05",
    )

    assert edu.name == "Bachelor of Science in Computer Science"
    assert edu.organization == "University Name"
    assert edu.degree == "Bachelor of Science"
    assert edu.start_date == "2018-09"
    assert edu.end_date == "2022-05"
    # Verify slug is generated
    assert edu.slug
    assert len(edu.slug.split("-")[-1]) == 6  # 6-char hash


def test_education_frontmatter_serialization():
    """Test education frontmatter serialization."""
    edu = Education(
        name="Master of Science",
        organization="University Name",
        degree="Master of Science",
        certificate="Data Science Certificate",
        start_date="2020-09",
        end_date="2022-05",
    )

    frontmatter_dict = edu.to_frontmatter_dict()

    assert frontmatter_dict["name"] == "Master of Science"
    assert frontmatter_dict["slug"] == edu.slug
    assert frontmatter_dict["organization"] == "University Name"
    assert frontmatter_dict["degree"] == "Master of Science"
    assert frontmatter_dict["certificate"] == "Data Science Certificate"
    assert frontmatter_dict["start_date"] == "2020-09"
    assert frontmatter_dict["end_date"] == "2022-05"


def test_education_optional_fields():
    """Test education with optional fields."""
    edu = Education(
        name="Certificate Program",
        certificate="AWS Solutions Architect",
    )

    assert edu.name == "Certificate Program"
    assert edu.certificate == "AWS Solutions Architect"
    assert edu.degree is None
    assert edu.organization is None
    assert edu.start_date is None
    assert edu.end_date is None


def test_education_from_frontmatter_dict():
    """Test creating education from frontmatter dictionary."""
    data = {
        "name": "Bachelor of Science",
        "organization": "University Name",
        "degree": "Bachelor of Science",
        "start_date": "2018-09",
        "end_date": "2022-05",
    }
    content = "Additional details about the degree program."

    edu = Education.from_frontmatter_dict(data, content)

    assert edu.name == "Bachelor of Science"
    assert edu.organization == "University Name"
    assert edu.degree == "Bachelor of Science"
    assert edu.start_date == "2018-09"
    assert edu.end_date == "2022-05"
    assert edu.content == "Additional details about the degree program."


def test_education_date_validator_truncates_yyyy_mm_dd():
    """Test that YYYY-MM-DD dates are truncated to YYYY-MM."""
    edu = Education(
        name="Bachelor of Science",
        start_date="2018-09-01",
        end_date="2022-05-15",
    )
    assert edu.start_date == "2018-09"
    assert edu.end_date == "2022-05"


def test_education_date_validator_passes_yyyy_mm():
    """Test that YYYY-MM dates pass through unchanged."""
    edu = Education(
        name="Bachelor of Science",
        start_date="2018-09",
        end_date="2022-05",
    )
    assert edu.start_date == "2018-09"
    assert edu.end_date == "2022-05"


def test_education_date_validator_passes_yyyy():
    """Test that YYYY dates pass through."""
    edu = Education(
        name="Bachelor of Science",
        start_date="2018",
    )
    assert edu.start_date == "2018"


def test_education_date_validator_normalizes_present():
    """Test that 'present' (any case) is normalized to 'Present'."""
    edu1 = Education(name="Program", end_date="present")
    assert edu1.end_date == "Present"

    edu2 = Education(name="Program", end_date="PRESENT")
    assert edu2.end_date == "Present"


def test_education_date_validator_none_passes():
    """Test that None dates pass through."""
    edu = Education(
        name="Program",
        start_date=None,
        end_date=None,
    )
    assert edu.start_date is None
    assert edu.end_date is None
