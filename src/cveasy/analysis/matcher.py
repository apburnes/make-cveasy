"""Keyword and skills matching algorithms."""

import re
from typing import List, Set, Dict
from collections import Counter


class KeywordMatcher:
    """Extract and match keywords from text."""

    def __init__(self):
        """Initialize keyword matcher."""
        # Common stop words to filter out
        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
            "been", "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "should", "could", "may", "might", "must", "can", "this",
            "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
        }

    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text.

        Args:
            text: Input text
            min_length: Minimum keyword length

        Returns:
            List of keywords
        """
        # Convert to lowercase and split
        words = re.findall(r'\b[a-z]+\b', text.lower())

        # Filter stop words and short words
        keywords = [
            word for word in words
            if word not in self.stop_words and len(word) >= min_length
        ]

        return keywords

    def get_keyword_frequency(self, text: str) -> Dict[str, int]:
        """
        Get keyword frequency in text.

        Args:
            text: Input text

        Returns:
            Dictionary mapping keywords to frequencies
        """
        keywords = self.extract_keywords(text)
        return dict(Counter(keywords))

    def match_keywords(self, resume_text: str, job_text: str) -> Dict[str, any]:
        """
        Match keywords between resume and job description.

        Args:
            resume_text: Resume text
            job_text: Job description text

        Returns:
            Dictionary with match statistics
        """
        resume_keywords = set(self.extract_keywords(resume_text))
        job_keywords = set(self.extract_keywords(job_text))

        # Find matching keywords
        matching_keywords = resume_keywords.intersection(job_keywords)

        # Find missing keywords
        missing_keywords = job_keywords - resume_keywords

        # Calculate match score
        if len(job_keywords) == 0:
            match_score = 0.0
        else:
            match_score = len(matching_keywords) / len(job_keywords) * 100

        return {
            "match_score": match_score,
            "matching_keywords": sorted(matching_keywords),
            "missing_keywords": sorted(missing_keywords),
            "total_job_keywords": len(job_keywords),
            "matched_count": len(matching_keywords),
            "missing_count": len(missing_keywords),
        }


class SkillsMatcher:
    """Match skills between resume and job description."""

    def __init__(self):
        """Initialize skills matcher."""
        # Common technical skills patterns
        self.skill_patterns = [
            r'\b(python|java|javascript|typescript|go|rust|c\+\+|c#|ruby|php|swift|kotlin)\b',
            r'\b(react|vue|angular|node\.js|django|flask|spring|express)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|terraform|ansible)\b',
            r'\b(sql|postgresql|mysql|mongodb|redis|elasticsearch)\b',
            r'\b(git|github|gitlab|jenkins|ci/cd|devops)\b',
            r'\b(agile|scrum|kanban|jira|confluence)\b',
            r'\b(machine learning|ml|ai|deep learning|nlp|computer vision)\b',
            r'\b(rest api|graphql|microservices|api design)\b',
        ]

    def extract_skills(self, text: str) -> Set[str]:
        """
        Extract skills from text.

        Args:
            text: Input text

        Returns:
            Set of extracted skills
        """
        skills = set()
        text_lower = text.lower()

        # Match against patterns
        for pattern in self.skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            skills.update(matches)

        # Also look for capitalized technical terms
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        # Filter for likely technical terms (2-3 words, common tech names)
        for term in capitalized_terms:
            if 2 <= len(term.split()) <= 3:
                skills.add(term.lower())

        return skills

    def match_skills(self, resume_text: str, job_text: str, resume_skills: List[str]) -> Dict[str, any]:
        """
        Match skills between resume and job description.

        Args:
            resume_text: Resume text
            job_text: Job description text
            resume_skills: List of skill names from resume data

        Returns:
            Dictionary with match statistics
        """
        # Extract skills from text
        resume_skills_from_text = self.extract_skills(resume_text)
        job_skills = self.extract_skills(job_text)

        # Combine with explicit skills
        all_resume_skills = resume_skills_from_text.union(
            {skill.lower() for skill in resume_skills}
        )

        # Find matching skills
        matching_skills = all_resume_skills.intersection(job_skills)

        # Find missing skills
        missing_skills = job_skills - all_resume_skills

        # Calculate match score
        if len(job_skills) == 0:
            match_score = 0.0
        else:
            match_score = len(matching_skills) / len(job_skills) * 100

        return {
            "match_score": match_score,
            "matching_skills": sorted(matching_skills),
            "missing_skills": sorted(missing_skills),
            "total_job_skills": len(job_skills),
            "matched_count": len(matching_skills),
            "missing_count": len(missing_skills),
        }
