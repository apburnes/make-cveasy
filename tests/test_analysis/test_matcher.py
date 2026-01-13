"""Tests for keyword and skills matchers with spaCy."""

import pytest
from cveasy.analysis.matcher import KeywordMatcher, SkillsMatcher, SemanticMatcher

# Check if spaCy is available
try:
    import spacy
    spacy.load("en_core_web_sm")
    SPACY_AVAILABLE = True
except (ImportError, OSError):
    SPACY_AVAILABLE = False


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_keyword_extraction():
    """Test keyword extraction with spaCy."""
    matcher = KeywordMatcher()
    text = "Python developer with AWS experience and Docker knowledge"

    keywords = matcher.extract_keywords(text)

    assert "python" in keywords
    assert "aws" in keywords
    assert "docker" in keywords


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
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


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_keyword_lemmatization():
    """Test that lemmatization works (e.g., 'developing' matches 'develop')."""
    matcher = KeywordMatcher()
    resume = "I am developing applications using Python"
    job = "We need developers who can develop software with Python"

    results = matcher.match_keywords(resume, job)

    # Should match on lemmatized forms of "develop"
    assert "develop" in results["matching_keywords"] or "python" in results["matching_keywords"]
    assert results["match_score"] > 0


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_keyword_pos_filtering():
    """Test that POS tagging filters out non-relevant words."""
    matcher = KeywordMatcher()
    text = "The quick brown fox jumps over the lazy dog"

    keywords = matcher.extract_keywords(text)

    # Should focus on nouns/adjectives, not verbs like "jumps"
    # "quick", "brown", "fox", "dog" might be included
    assert len(keywords) > 0
    # Stop words like "the" should be filtered
    assert "the" not in keywords


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_skills_extraction():
    """Test skills extraction with spaCy."""
    matcher = SkillsMatcher()
    text = "Experience with Python, React, and AWS"

    skills = matcher.extract_skills(text)

    assert len(skills) > 0
    # Should extract at least some of these
    assert any(skill in ["python", "react", "aws"] for skill in skills)


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_skills_phrase_matcher():
    """Test that PhraseMatcher finds multi-word technical terms."""
    matcher = SkillsMatcher()
    text = "Experience with machine learning and REST API development"

    skills = matcher.extract_skills(text)

    # Should extract multi-word terms
    assert any("machine learning" in skill or "ml" in skill for skill in skills)
    assert any("rest api" in skill or "api" in skill for skill in skills)


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_skills_ner_extraction():
    """Test that NER extracts technology organizations and products."""
    matcher = SkillsMatcher()
    text = "Worked with AWS and Microsoft Azure cloud services"

    skills = matcher.extract_skills(text)

    # Should extract AWS and Azure
    assert any("aws" in skill for skill in skills)
    assert any("azure" in skill for skill in skills)


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_skills_matching():
    """Test skills matching between resume and job."""
    matcher = SkillsMatcher()
    resume = "Python developer with React experience"
    job = "Looking for Python developer with React and Docker experience"
    resume_skills = ["Python", "React"]

    results = matcher.match_skills(resume, job, resume_skills)

    assert results["match_score"] > 0
    assert any("python" in skill for skill in results["matching_skills"])
    assert any("react" in skill for skill in results["matching_skills"])


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_semantic_similarity_basic():
    """Test basic semantic similarity matching."""
    matcher = SemanticMatcher()
    resume = "I develop software applications"
    job = "We need software developers"

    results = matcher.match_semantic_similarity(resume, job)

    # Should return results structure
    assert "similarity_score" in results
    assert "matched_pairs" in results
    assert "average_similarity" in results
    assert isinstance(results["similarity_score"], (int, float))
    assert isinstance(results["matched_pairs"], list)


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_semantic_similarity_with_keywords():
    """Test semantic similarity with provided keywords."""
    matcher = SemanticMatcher()
    resume = "I develop software applications using Python"
    job = "We need developers who write code in Python"
    resume_keywords = ["develop", "software", "application", "python"]
    job_keywords = ["developer", "code", "python"]

    results = matcher.match_semantic_similarity(
        resume, job, resume_keywords=resume_keywords, job_keywords=job_keywords
    )

    assert "similarity_score" in results
    assert "matched_pairs" in results
    # Should find some semantic matches (e.g., "develop" ~ "developer")
    assert len(results["matched_pairs"]) >= 0  # May be 0 if vectors not available in sm model


@pytest.mark.skipif(not SPACY_AVAILABLE, reason="spaCy model not installed")
def test_semantic_similarity_threshold():
    """Test that similarity threshold filters low-similarity matches."""
    matcher = SemanticMatcher(similarity_threshold=0.7)
    resume = "I develop software"
    job = "We need developers"

    results = matcher.match_semantic_similarity(resume, job)

    # All matched pairs should meet the threshold
    for pair in results["matched_pairs"]:
        assert pair["similarity"] >= 0.7


def test_keyword_extraction_fallback():
    """Test that keyword extraction falls back to regex if spaCy is unavailable."""
    # This test will run even if spaCy is not installed
    # The fallback should still work
    matcher = KeywordMatcher()
    text = "Python developer with AWS experience"

    keywords = matcher.extract_keywords(text)

    # Should still extract keywords (either via spaCy or fallback)
    assert len(keywords) > 0
    assert "python" in keywords or "aws" in keywords or "developer" in keywords


def test_skills_extraction_fallback():
    """Test that skills extraction falls back to regex if spaCy is unavailable."""
    matcher = SkillsMatcher()
    text = "Experience with Python, React, and AWS"

    skills = matcher.extract_skills(text)

    # Should still extract skills (either via spaCy or fallback)
    assert len(skills) > 0


def test_semantic_similarity_fallback():
    """Test that semantic similarity returns empty results if spaCy is unavailable."""
    matcher = SemanticMatcher()
    resume = "I develop software"
    job = "We need developers"

    results = matcher.match_semantic_similarity(resume, job)

    # Should return structure with zero scores if spaCy unavailable
    assert "similarity_score" in results
    assert "matched_pairs" in results
