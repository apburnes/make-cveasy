"""Tests for ResumeChecker class."""

import pytest
from unittest.mock import MagicMock, patch
from cveasy.analysis.checker import ResumeChecker
from cveasy.models.job import Job
from cveasy.models.skill import Skill


@pytest.fixture
def mock_provider():
    """Create a mock AI provider."""
    provider = MagicMock()
    provider.generate.return_value = """Overall fit score: 85/100

Top 3 strengths:
1. Strong Python experience
2. AWS cloud expertise
3. Leadership skills

Top 3 areas for improvement:
1. Add more Docker experience
2. Emphasize microservices work
3. Include more metrics

Specific suggestions:
- Add more details about containerization
- Highlight scalability achievements

Missing keywords: Docker, Kubernetes, CI/CD

Recommendations:
- Add Docker to skills section
- Include CI/CD pipeline experience"""
    return provider


@pytest.fixture
def mock_keyword_matcher():
    """Create a mock keyword matcher."""
    matcher = MagicMock()
    matcher.match_keywords.return_value = {
        "match_score": 75.5,
        "matched_count": 15,
        "total_job_keywords": 20,
        "missing_count": 5,
        "matching_keywords": ["Python", "AWS", "Docker", "API"],
        "missing_keywords": ["Kubernetes", "CI/CD", "Terraform", "Monitoring", "Scaling"],
    }
    return matcher


@pytest.fixture
def mock_skills_matcher():
    """Create a mock skills matcher."""
    matcher = MagicMock()
    matcher.match_skills.return_value = {
        "match_score": 80.0,
        "matched_count": 8,
        "total_job_skills": 10,
        "missing_count": 2,
        "matching_skills": ["Python", "AWS", "Docker", "PostgreSQL"],
        "missing_skills": ["Kubernetes", "Terraform"],
    }
    return matcher


def test_resume_checker_init_default(mock_provider):
    """Test ResumeChecker initialization with default provider."""
    with patch("cveasy.analysis.checker.get_ai_provider", return_value=mock_provider):
        checker = ResumeChecker()
        assert checker.provider == mock_provider
        assert checker.keyword_matcher is not None
        assert checker.skills_matcher is not None


def test_resume_checker_init_with_provider(
    mock_provider, mock_keyword_matcher, mock_skills_matcher
):
    """Test ResumeChecker initialization with explicit provider."""
    checker = ResumeChecker(provider=mock_provider)
    assert checker.provider == mock_provider


def test_check_method(mock_provider, mock_keyword_matcher, mock_skills_matcher):
    """Test check method generates report."""
    checker = ResumeChecker(provider=mock_provider)
    checker.keyword_matcher = mock_keyword_matcher
    checker.skills_matcher = mock_skills_matcher

    resume_text = "# Resume\n\nPython developer with AWS experience"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS, Docker, Kubernetes",
        pay="$150k-200k",
        content="Looking for a Python developer with AWS and Docker experience",
    )
    skills = [
        Skill(
            name="Python",
            category="Programming",
            years=5,
            proficiency="Expert",
            related_experiences=[],
            content="",
        ),
        Skill(
            name="AWS",
            category="Cloud",
            years=3,
            proficiency="Advanced",
            related_experiences=[],
            content="",
        ),
    ]

    report = checker.check(resume_text, job, skills)

    assert report is not None
    assert "# Resume Quality Check Report" in report
    assert "Software Engineer" in report
    assert "75.5" in report  # Match score
    assert "80.0" in report  # Skills match score

    # Verify matchers were called
    mock_keyword_matcher.match_keywords.assert_called_once_with(resume_text, job.content)
    mock_skills_matcher.match_skills.assert_called_once_with(
        resume_text, job.content, ["Python", "AWS"]
    )

    # Verify LLM was called
    mock_provider.generate.assert_called_once()


def test_check_method_with_missing_keywords(
    mock_provider, mock_keyword_matcher, mock_skills_matcher
):
    """Test check method with missing keywords."""
    checker = ResumeChecker(provider=mock_provider)
    checker.keyword_matcher = mock_keyword_matcher
    checker.skills_matcher = mock_skills_matcher

    resume_text = "# Resume\n\nBasic experience"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS, Docker",
        pay="$150k-200k",
        content="Job description",
    )
    skills = []

    report = checker.check(resume_text, job, skills)

    assert "Missing Keywords" in report
    assert "Kubernetes" in report or "missing" in report.lower()


def test_check_method_with_missing_skills(mock_provider, mock_keyword_matcher, mock_skills_matcher):
    """Test check method with missing skills."""
    checker = ResumeChecker(provider=mock_provider)
    checker.keyword_matcher = mock_keyword_matcher
    checker.skills_matcher = mock_skills_matcher

    resume_text = "# Resume\n\nContent"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS, Docker",
        pay="$150k-200k",
        content="Job description",
    )
    skills = [
        Skill(
            name="Python",
            category="Programming",
            years=5,
            proficiency="Expert",
            related_experiences=[],
            content="",
        )
    ]

    report = checker.check(resume_text, job, skills)

    assert "Missing Skills" in report


def test_check_method_report_structure(mock_provider, mock_keyword_matcher, mock_skills_matcher):
    """Test check method report structure."""
    checker = ResumeChecker(provider=mock_provider)
    checker.keyword_matcher = mock_keyword_matcher
    checker.skills_matcher = mock_skills_matcher

    resume_text = "# Resume\n\nContent"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )
    skills = []

    report = checker.check(resume_text, job, skills)

    # Check report sections
    assert "# Resume Quality Check Report" in report
    assert "## Quantitative Metrics" in report
    assert "## Detailed Analysis" in report
    assert "## Missing Keywords" in report
    assert "## Missing Skills" in report
    assert "## Matching Keywords" in report
    assert "## Matching Skills" in report


def test_check_method_with_no_missing_keywords(mock_provider):
    """Test check method when no keywords are missing."""
    keyword_matcher = MagicMock()
    keyword_matcher.match_keywords.return_value = {
        "match_score": 100.0,
        "matched_count": 20,
        "total_job_keywords": 20,
        "missing_count": 0,
        "matching_keywords": ["Python", "AWS", "Docker"],
        "missing_keywords": [],
    }

    skills_matcher = MagicMock()
    skills_matcher.match_skills.return_value = {
        "match_score": 100.0,
        "matched_count": 10,
        "total_job_skills": 10,
        "missing_count": 0,
        "matching_skills": ["Python", "AWS"],
        "missing_skills": [],
    }

    checker = ResumeChecker(provider=mock_provider)
    checker.keyword_matcher = keyword_matcher
    checker.skills_matcher = skills_matcher

    resume_text = "# Resume\n\nContent"
    job = Job(
        name="Software Engineer",
        title="Senior Software Engineer",
        location="Remote",
        requirements="Python, AWS",
        pay="$150k-200k",
        content="Job description",
    )
    skills = []

    report = checker.check(resume_text, job, skills)

    assert "No missing keywords found" in report
    assert "No missing skills found" in report
