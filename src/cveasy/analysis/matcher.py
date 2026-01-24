"""Keyword and skills matching algorithms using spaCy NLP."""

import re
from typing import List, Set, Dict, Optional
from collections import Counter

try:
    import spacy
    from spacy.matcher import PhraseMatcher
    from spacy.tokens import Doc
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False

from cveasy.config import get_spacy_model


def _load_spacy_model(model_name: str = "en_core_web_sm"):
    """
    Load spaCy model with validation and helpful error messages.

    Args:
        model_name: Name of the spaCy model to load

    Returns:
        Loaded spaCy model

    Raises:
        OSError: If model is not installed, with instructions to download it
    """
    if not SPACY_AVAILABLE:
        raise ImportError(
            "spaCy is not installed. Please install it with: pip install spacy>=3.8.0"
        )

    try:
        nlp = spacy.load(model_name)
        return nlp
    except OSError:
        raise OSError(
            f"spaCy model '{model_name}' is not installed. "
            f"Please download it by running: python -m spacy download {model_name}\n"
            f"See README.md for installation instructions."
        )


class KeywordMatcher:
    """Extract and match keywords from text using spaCy NLP."""

    _nlp_cache = {}  # Cache models by name

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize keyword matcher.

        Args:
            model_name: spaCy model to use (default: from CVEASY_SPACY_MODEL env var or en_core_web_sm)
        """
        self._model_name = model_name if model_name is not None else get_spacy_model()
        # Model will be loaded lazily on first use

    @classmethod
    def _get_nlp(cls, model_name: str = "en_core_web_sm"):
        """
        Get or load spaCy model (cached).

        Args:
            model_name: Name of the spaCy model

        Returns:
            Loaded spaCy model
        """
        if model_name not in cls._nlp_cache:
            cls._nlp_cache[model_name] = _load_spacy_model(model_name)
        return cls._nlp_cache[model_name]

    def extract_keywords(self, text: str, min_length: int = 3) -> List[str]:
        """
        Extract keywords from text using spaCy lemmatization and POS tagging.

        Args:
            text: Input text
            min_length: Minimum keyword length

        Returns:
            List of keywords (lemmatized)
        """
        if not SPACY_AVAILABLE:
            # Fallback to simple regex-based extraction if spaCy is not available
            words = re.findall(r'\b[a-z]+\b', text.lower())
            stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
                "been", "being", "have", "has", "had", "do", "does", "did", "will",
                "would", "should", "could", "may", "might", "must", "can", "this",
                "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
            }
            keywords = [
                word for word in words
                if word not in stop_words and len(word) >= min_length
            ]
            return keywords

        try:
            nlp = self._get_nlp(self._model_name)
            doc = nlp(text)
        except (OSError, ImportError):
            # Model not installed or spaCy not available, use fallback
            words = re.findall(r'\b[a-z]+\b', text.lower())
            stop_words = {
                "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
                "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
                "been", "being", "have", "has", "had", "do", "does", "did", "will",
                "would", "should", "could", "may", "might", "must", "can", "this",
                "that", "these", "those", "i", "you", "he", "she", "it", "we", "they",
            }
            keywords = [
                word for word in words
                if word not in stop_words and len(word) >= min_length
            ]
            return keywords

        keywords = []
        # Focus on nouns, proper nouns, and adjectives
        # POS tags: NOUN, PROPN (proper noun), ADJ (adjective)
        for token in doc:
            # Skip stop words, punctuation, and short tokens
            if (
                not token.is_stop
                and not token.is_punct
                and not token.is_space
                and len(token.text) >= min_length
                and token.pos_ in ("NOUN", "PROPN", "ADJ")
            ):
                # Use lemmatized form for normalization
                lemma = token.lemma_.lower()
                if len(lemma) >= min_length:
                    keywords.append(lemma)

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
        Match keywords between resume and job description using lemmatization.

        Args:
            resume_text: Resume text
            job_text: Job description text

        Returns:
            Dictionary with match statistics
        """
        resume_keywords = set(self.extract_keywords(resume_text))
        job_keywords = set(self.extract_keywords(job_text))

        # Find matching keywords (lemmatized forms match)
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
    """Match skills between resume and job description using spaCy NER and PhraseMatcher."""

    _nlp_cache = {}  # Cache models by name
    _phrase_matcher_cache = {}  # Cache phrase matchers by model name

    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize skills matcher.

        Args:
            model_name: spaCy model to use (default: from CVEASY_SPACY_MODEL env var or en_core_web_sm)
        """
        self._model_name = model_name if model_name is not None else get_spacy_model()
        # Common technical skills patterns for PhraseMatcher
        self.skill_patterns = [
            "python", "java", "javascript", "typescript", "go", "rust", "c++", "c#", "ruby", "php", "swift", "kotlin",
            "react", "vue", "angular", "node.js", "django", "flask", "spring", "express",
            "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
            "sql", "postgresql", "mysql", "mongodb", "redis", "elasticsearch",
            "git", "github", "gitlab", "jenkins", "ci/cd", "devops",
            "agile", "scrum", "kanban", "jira", "confluence",
            "machine learning", "ml", "ai", "deep learning", "nlp", "computer vision",
            "rest api", "graphql", "microservices", "api design",
        ]

    @classmethod
    def _get_nlp(cls, model_name: str = "en_core_web_sm"):
        """
        Get or load spaCy model (cached).

        Args:
            model_name: Name of the spaCy model

        Returns:
            Loaded spaCy model
        """
        if model_name not in cls._nlp_cache:
            cls._nlp_cache[model_name] = _load_spacy_model(model_name)
        return cls._nlp_cache[model_name]

    def _get_phrase_matcher(self, nlp, model_name: str):
        """
        Get or create PhraseMatcher for technical terms (cached per model).

        Args:
            nlp: spaCy language model
            model_name: Name of the model (for caching)

        Returns:
            PhraseMatcher instance
        """
        if model_name not in self._phrase_matcher_cache:
            phrase_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
            # Add skill patterns to matcher
            patterns = [nlp.make_doc(skill) for skill in self.skill_patterns]
            phrase_matcher.add("SKILLS", patterns)
            self._phrase_matcher_cache[model_name] = phrase_matcher
        return self._phrase_matcher_cache[model_name]

    def extract_skills(self, text: str) -> Set[str]:
        """
        Extract skills from text using spaCy NER and PhraseMatcher.

        Args:
            text: Input text

        Returns:
            Set of extracted skills
        """
        if not SPACY_AVAILABLE:
            # Fallback to regex-based extraction
            skills = set()
            text_lower = text.lower()
            skill_patterns_regex = [
                r'\b(python|java|javascript|typescript|go|rust|c\+\+|c#|ruby|php|swift|kotlin)\b',
                r'\b(react|vue|angular|node\.js|django|flask|spring|express)\b',
                r'\b(aws|azure|gcp|docker|kubernetes|terraform|ansible)\b',
                r'\b(sql|postgresql|mysql|mongodb|redis|elasticsearch)\b',
                r'\b(git|github|gitlab|jenkins|ci/cd|devops)\b',
                r'\b(agile|scrum|kanban|jira|confluence)\b',
                r'\b(machine learning|ml|ai|deep learning|nlp|computer vision)\b',
                r'\b(rest api|graphql|microservices|api design)\b',
            ]
            for pattern in skill_patterns_regex:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                skills.update(matches)
            capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            for term in capitalized_terms:
                if 2 <= len(term.split()) <= 3:
                    skills.add(term.lower())
            return skills

        try:
            nlp = self._get_nlp(self._model_name)
            doc = nlp(text)
        except (OSError, ImportError):
            # Model not installed or spaCy not available, use fallback
            skills = set()
            text_lower = text.lower()
            skill_patterns_regex = [
                r'\b(python|java|javascript|typescript|go|rust|c\+\+|c#|ruby|php|swift|kotlin)\b',
                r'\b(react|vue|angular|node\.js|django|flask|spring|express)\b',
                r'\b(aws|azure|gcp|docker|kubernetes|terraform|ansible)\b',
                r'\b(sql|postgresql|mysql|mongodb|redis|elasticsearch)\b',
                r'\b(git|github|gitlab|jenkins|ci/cd|devops)\b',
                r'\b(agile|scrum|kanban|jira|confluence)\b',
                r'\b(machine learning|ml|ai|deep learning|nlp|computer vision)\b',
                r'\b(rest api|graphql|microservices|api design)\b',
            ]
            for pattern in skill_patterns_regex:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                skills.update(matches)
            capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            for term in capitalized_terms:
                if 2 <= len(term.split()) <= 3:
                    skills.add(term.lower())
            return skills

        skills = set()

        # Use PhraseMatcher for known technical terms
        phrase_matcher = self._get_phrase_matcher(nlp, self._model_name)
        matches = phrase_matcher(doc)
        for match_id, start, end in matches:
            skill_text = doc[start:end].text.lower()
            skills.add(skill_text)

        # Use NER to extract organizations (often technology companies)
        for ent in doc.ents:
            if ent.label_ in ("ORG", "PRODUCT"):
                # Filter for likely technical terms
                ent_text = ent.text.lower()
                if len(ent_text) >= 2 and len(ent_text.split()) <= 3:
                    skills.add(ent_text)

        # Extract noun phrases that might be technical terms
        for chunk in doc.noun_chunks:
            chunk_text = chunk.text.lower()
            # Look for 2-3 word noun phrases that might be technologies
            if 2 <= len(chunk_text.split()) <= 3:
                # Check if it contains technical indicators
                if any(
                    token.pos_ in ("NOUN", "PROPN")
                    and not token.is_stop
                    for token in chunk
                ):
                    skills.add(chunk_text)

        # Also look for capitalized technical terms (fallback)
        capitalized_terms = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
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


class SemanticMatcher:
    """Semantic similarity matching using spaCy word vectors."""

    _nlp_cache = {}  # Cache models by name

    def __init__(self, model_name: Optional[str] = None, similarity_threshold: float = 0.5):
        """
        Initialize semantic matcher.

        Args:
            model_name: spaCy model to use (default: from CVEASY_SPACY_MODEL env var or en_core_web_sm)
            similarity_threshold: Minimum similarity score (0.0-1.0) for matches
        """
        self._model_name = model_name if model_name is not None else get_spacy_model()
        self.similarity_threshold = similarity_threshold

    @classmethod
    def _get_nlp(cls, model_name: str = "en_core_web_sm"):
        """
        Get or load spaCy model (cached).

        Args:
            model_name: Name of the spaCy model

        Returns:
            Loaded spaCy model
        """
        if model_name not in cls._nlp_cache:
            cls._nlp_cache[model_name] = _load_spacy_model(model_name)
        return cls._nlp_cache[model_name]

    def match_semantic_similarity(
        self,
        resume_text: str,
        job_text: str,
        resume_keywords: Optional[List[str]] = None,
        job_keywords: Optional[List[str]] = None,
    ) -> Dict[str, any]:
        """
        Calculate semantic similarity between resume and job description.

        Note: This requires a spaCy model with word vectors (en_core_web_md or en_core_web_lg).
        The small model (en_core_web_sm) doesn't include vectors, so this will return
        a similarity score of 0.0 if vectors are not available.

        Args:
            resume_text: Resume text
            job_text: Job description text
            resume_keywords: Optional list of resume keywords (if None, extracts them)
            job_keywords: Optional list of job keywords (if None, extracts them)

        Returns:
            Dictionary with similarity scores and matched terms
        """
        if not SPACY_AVAILABLE:
            return {
                "similarity_score": 0.0,
                "matched_pairs": [],
                "average_similarity": 0.0,
            }

        try:
            nlp = self._get_nlp(self._model_name)
            resume_doc = nlp(resume_text)
            job_doc = nlp(job_text)
        except (OSError, ImportError):
            # Model not installed or spaCy not available
            return {
                "similarity_score": 0.0,
                "matched_pairs": [],
                "average_similarity": 0.0,
            }

        # Check if vectors are available
        if not resume_doc.has_vector or not job_doc.has_vector:
            # Model doesn't have vectors, return empty results
            return {
                "similarity_score": 0.0,
                "matched_pairs": [],
                "average_similarity": 0.0,
                "note": "Word vectors not available in this model. Use en_core_web_md or en_core_web_lg for semantic similarity.",
            }

        # Calculate overall document similarity
        doc_similarity = resume_doc.similarity(job_doc)

        # Extract keywords if not provided
        if resume_keywords is None:
            keyword_matcher = KeywordMatcher(self._model_name)
            resume_keywords = keyword_matcher.extract_keywords(resume_text)
        if job_keywords is None:
            keyword_matcher = KeywordMatcher(self._model_name)
            job_keywords = keyword_matcher.extract_keywords(job_text)

        # Calculate similarity between keyword pairs
        matched_pairs = []
        similarities = []

        for resume_keyword in resume_keywords:
            resume_token = nlp(resume_keyword)
            if not resume_token.has_vector:
                continue

            best_match = None
            best_similarity = 0.0

            for job_keyword in job_keywords:
                job_token = nlp(job_keyword)
                if not job_token.has_vector:
                    continue

                similarity = resume_token.similarity(job_token)
                if similarity > best_similarity and similarity >= self.similarity_threshold:
                    best_similarity = similarity
                    best_match = job_keyword

            if best_match:
                matched_pairs.append({
                    "resume_keyword": resume_keyword,
                    "job_keyword": best_match,
                    "similarity": best_similarity,
                })
                similarities.append(best_similarity)

        average_similarity = sum(similarities) / len(similarities) if similarities else 0.0

        return {
            "similarity_score": doc_similarity * 100,  # Convert to percentage
            "matched_pairs": matched_pairs,
            "average_similarity": average_similarity * 100,  # Convert to percentage
            "matched_count": len(matched_pairs),
        }
