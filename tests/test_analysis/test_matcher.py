"""Tests for keyword and skills matchers."""

from cveasy.analysis.matcher import KeywordMatcher, SkillsMatcher


def test_keyword_extraction():
    """Test keyword extraction."""
    matcher = KeywordMatcher()
    text = "Python developer with AWS experience and Docker knowledge"

    keywords = matcher.extract_keywords(text)

    assert "python" in keywords
    assert "aws" in keywords
    assert "docker" in keywords


def test_keyword_matching():
    """Test keyword matching between resume and job."""
    matcher = KeywordMatcher()
    resume = "Python developer with AWS experience"
    job = "Looking for Python developer with AWS and Docker experience"

    results = matcher.match_keywords(resume, job)

    assert results["match_score"] > 0
    assert "python" in results["matching_keywords"]
    assert "aws" in results["matching_keywords"]
    assert "docker" in results["missing_keywords"]


def test_skills_extraction():
    """Test skills extraction."""
    matcher = SkillsMatcher()
    text = "Experience with Python, React, and AWS"

    skills = matcher.extract_skills(text)

    assert len(skills) > 0
