"""Resume parser for extracting structured data from PDF/DOCX files."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from slugify import slugify

from cveasy.ai.providers import AIProvider
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.project import Project
from cveasy.models.story import Story
from cveasy.models.education import Education
from cveasy.models.link import Link
from cveasy.models.bio import Bio
from cveasy.exceptions import AIProviderError, DataImportError, ValidationError

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text from a PDF file.

    Args:
        file_path: Path to the PDF file

    Returns:
        Extracted text content

    Raises:
        DataImportError: If file not found or extraction fails
        ValidationError: If pypdf is not installed
    """
    try:
        from pypdf import PdfReader
    except ImportError:
        raise ValidationError("pypdf package is required. Install with: pip install pypdf")

    if not file_path.exists():
        raise DataImportError(f"PDF file not found: {file_path}")

    try:
        reader = PdfReader(str(file_path))
        text_parts = []
        for page in reader.pages:
            text_parts.append(page.extract_text())
        return "\n".join(text_parts)
    except (OSError, ValueError) as e:
        raise DataImportError(f"Failed to extract text from PDF: {e}") from e


def extract_text_from_docx(file_path: Path) -> str:
    """
    Extract text from a DOCX file.

    Args:
        file_path: Path to the DOCX file

    Returns:
        Extracted text content

    Raises:
        DataImportError: If file not found or extraction fails
        ValidationError: If python-docx is not installed
    """
    try:
        from docx import Document
    except ImportError:
        raise ValidationError(
            "python-docx package is required. Install with: pip install python-docx"
        )

    if not file_path.exists():
        raise DataImportError(f"DOCX file not found: {file_path}")

    try:
        doc = Document(str(file_path))
        text_parts = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
        return "\n".join(text_parts)
    except (OSError, ValueError, KeyError) as e:
        raise DataImportError(f"Failed to extract text from DOCX: {e}") from e


def parse_resume_with_llm(text: str, provider: AIProvider) -> Dict:
    """
    Parse resume text using LLM to extract structured data.

    Args:
        text: Resume text content
        provider: AI provider instance

    Returns:
        Dictionary with parsed data containing skills, experiences, projects, and stories

    Raises:
        ValueError: If LLM response cannot be parsed as JSON
    """
    system_prompt = """You are a resume parser. Extract structured information from resume text and return it as valid JSON.
You must return ONLY valid JSON, no additional text or markdown formatting."""

    prompt = f"""Parse the following resume text and extract structured information. Return a JSON object with the following structure:

{{
  "bio": {{
    "name": "Full name from resume header",
    "location": "City, State/Country from resume header (if available)"
  }},
  "skills": [
    {{
      "name": "Skill name",
      "category": "Category (e.g., Programming Language, Framework, Tool)",
      "years": 5,
      "proficiency": "Beginner|Intermediate|Advanced|Expert",
      "related_experience": ["Job title 1", "Job title 2"]
    }}
  ],
  "experiences": [
    {{
      "title": "Job title",
      "organization": "Company name",
      "start_date": "YYYY-MM-DD or YYYY-MM",
      "end_date": "YYYY-MM-DD, YYYY-MM, or 'Present'",
      "location": "City, State/Country",
      "content": "Detailed description of responsibilities and achievements",
      "related_skills": ["Skill name 1", "Skill name 2"],
      "related_stories": ["Story title 1", "Story title 2"]
    }}
  ],
  "projects": [
    {{
      "name": "Project name",
      "description": "Brief description",
      "link": "URL if available",
      "content": "Detailed project description"
    }}
  ],
  "stories": [
    {{
      "title": "Achievement/story title",
      "context": "Context or situation",
      "outcome": "Result or outcome",
      "content": "Detailed description"
    }}
  ],
  "education": [
    {{
      "name": "Education name/title",
      "start_date": "YYYY-MM-DD or YYYY-MM",
      "end_date": "YYYY-MM-DD, YYYY-MM, or 'Present'",
      "degree": "Degree type (e.g., Bachelor of Science)",
      "certificate": "Certificate name",
      "organization": "School/institution name",
      "content": "Additional description"
    }}
  ],
  "links": [
    {{
      "name": "Link name (e.g., LinkedIn, GitHub)",
      "description": "Description of the link",
      "url": "URL"
    }}
  ]
}}

IMPORTANT: For relationships:
- In "experiences", include "related_skills" (array of skill names used in this role) and "related_stories" (array of story/achievement titles from this role)
- In "skills", include "related_experience" (array of job titles where this skill was used)
- Use the exact names/titles as they appear in the respective arrays (e.g., if a skill is named "Python", reference it as "Python" in related_skills)
- If no relationships exist, use an empty array []

Resume text:
{text}

Extract all relevant information. If a field is not available, use null or empty string. Return ONLY the JSON object, no markdown code blocks or additional text."""

    try:
        logger.debug("Parsing resume with LLM (%d chars of text)", len(text))
        response = provider.generate(prompt, system_prompt)

        # Remove markdown code blocks if present
        response = response.strip()
        response = re.sub(r"^```(?:json)?\s*\n?", "", response)
        response = re.sub(r"\n?\s*```$", "", response)
        response = response.strip()

        parsed_data = json.loads(response)

        # Ensure all expected keys exist
        if not isinstance(parsed_data, dict):
            raise ValidationError("LLM response is not a JSON object")

        # Initialize missing keys
        for key in ["bio", "skills", "experiences", "projects", "stories", "education", "links"]:
            if key not in parsed_data:
                if key == "bio":
                    parsed_data[key] = None
                else:
                    parsed_data[key] = []

        return parsed_data
    except json.JSONDecodeError as e:
        raise DataImportError(f"Failed to parse LLM response as JSON: {e}") from e
    except (AIProviderError, ValidationError) as e:
        raise DataImportError(f"Error parsing resume with LLM: {e}") from e


def create_models_from_parsed_data(
    parsed_data: Dict,
) -> Tuple[
    Optional[Bio],
    List[Skill],
    List[Experience],
    List[Project],
    List[Story],
    List[Education],
    List[Link],
]:
    """
    Create model objects from parsed resume data and establish relationships.

    Args:
        parsed_data: Dictionary with parsed resume data

    Returns:
        Tuple of (bio, skills, experiences, projects, stories, education, links) with relationships established
    """
    # Step 1: Create bio if available
    bio = None
    bio_data = parsed_data.get("bio")
    if bio_data and bio_data.get("name"):
        # Handle None values explicitly - convert to empty string
        # Use or "" to handle both None and empty string cases
        location = bio_data.get("location") or ""
        bio = Bio(
            name=bio_data.get("name", ""),
            location=location,
        )

    # Step 2: Create all models first
    skills = []
    for skill_data in parsed_data.get("skills", []):
        if not skill_data.get("name"):
            continue

        skill = Skill(
            name=skill_data.get("name", ""),
            category=skill_data.get("category"),
            years=skill_data.get("years"),
            proficiency=skill_data.get("proficiency"),
            related_experience=[],
            content="",
        )
        skills.append(skill)

    experiences = []
    for exp_data in parsed_data.get("experiences", []):
        if not exp_data.get("title") or not exp_data.get("organization"):
            continue

        experience = Experience(
            title=exp_data.get("title", ""),
            organization=exp_data.get("organization", ""),
            start_date=exp_data.get("start_date"),
            end_date=exp_data.get("end_date"),
            location=exp_data.get("location"),
            related_skills=[],
            related_stories=[],
            content=exp_data.get("content") or "",
        )
        experiences.append(experience)

    projects = []
    for proj_data in parsed_data.get("projects", []):
        if not proj_data.get("name"):
            continue

        project = Project(
            name=proj_data.get("name", ""),
            description=proj_data.get("description") or "",
            link=proj_data.get("link"),
            content=proj_data.get("content") or "",
        )
        projects.append(project)

    stories = []
    for story_data in parsed_data.get("stories", []):
        if not story_data.get("title"):
            continue

        story = Story(
            title=story_data.get("title", ""),
            context=story_data.get("context"),
            outcome=story_data.get("outcome"),
            content=story_data.get("content") or "",
        )
        stories.append(story)

    # Step 2: Build name-to-ID mapping dictionaries (using slugify for IDs)
    skill_name_to_id: Dict[str, str] = {}
    for skill in skills:
        skill_id = slugify(skill.name, lowercase=True)
        skill_name_to_id[skill.name.lower()] = skill_id
        # Also store original case for exact matching
        skill_name_to_id[skill.name] = skill_id

    story_title_to_id: Dict[str, str] = {}
    for story in stories:
        story_id = slugify(story.title, lowercase=True)
        story_title_to_id[story.title.lower()] = story_id
        # Also store original case for exact matching
        story_title_to_id[story.title] = story_id

    experience_title_to_id: Dict[str, str] = {}
    for experience in experiences:
        exp_id = slugify(experience.title, lowercase=True)
        experience_title_to_id[experience.title.lower()] = exp_id
        # Also store original case for exact matching
        experience_title_to_id[experience.title] = exp_id

    # Step 3: Process relationships from parsed data
    # Build lookup dictionaries to find models by name/title
    experience_by_title: Dict[str, Experience] = {}
    for experience in experiences:
        experience_by_title[experience.title] = experience
        experience_by_title[experience.title.lower()] = experience

    skill_by_name: Dict[str, Skill] = {}
    for skill in skills:
        skill_by_name[skill.name] = skill
        skill_by_name[skill.name.lower()] = skill

    # Process experiences -> skills and experiences -> stories
    for exp_data in parsed_data.get("experiences", []):
        if not exp_data.get("title") or not exp_data.get("organization"):
            continue

        # Find the experience by title (try exact match, then case-insensitive)
        exp_title = exp_data.get("title", "")
        experience = experience_by_title.get(exp_title) or experience_by_title.get(
            exp_title.lower()
        )
        if not experience:
            continue

        # Map related_skills names to skill IDs
        related_skill_names = exp_data.get("related_skills", [])
        if related_skill_names:
            for skill_name in related_skill_names:
                # Try exact match first, then case-insensitive
                skill_id = skill_name_to_id.get(skill_name) or skill_name_to_id.get(
                    skill_name.lower()
                )
                if skill_id and skill_id not in experience.related_skills:
                    experience.related_skills.append(skill_id)

        # Map related_stories titles to story IDs
        related_story_titles = exp_data.get("related_stories", [])
        if related_story_titles:
            for story_title in related_story_titles:
                # Try exact match first, then case-insensitive
                story_id = story_title_to_id.get(story_title) or story_title_to_id.get(
                    story_title.lower()
                )
                if story_id and story_id not in experience.related_stories:
                    experience.related_stories.append(story_id)

    # Process skills -> experiences
    for skill_data in parsed_data.get("skills", []):
        if not skill_data.get("name"):
            continue

        # Find the skill by name (try exact match, then case-insensitive)
        skill_name = skill_data.get("name", "")
        skill = skill_by_name.get(skill_name) or skill_by_name.get(skill_name.lower())
        if not skill:
            continue

        # Map related_experience titles to experience IDs
        related_exp_titles = skill_data.get("related_experience", [])
        if related_exp_titles:
            for exp_title in related_exp_titles:
                # Try exact match first, then case-insensitive
                exp_id = experience_title_to_id.get(exp_title) or experience_title_to_id.get(
                    exp_title.lower()
                )
                if exp_id and exp_id not in skill.related_experience:
                    skill.related_experience.append(exp_id)

    educations = []
    for edu_data in parsed_data.get("education", []):
        if not edu_data.get("name"):
            continue

        education = Education(
            name=edu_data.get("name", ""),
            start_date=edu_data.get("start_date"),
            end_date=edu_data.get("end_date"),
            degree=edu_data.get("degree"),
            certificate=edu_data.get("certificate"),
            organization=edu_data.get("organization"),
            content=edu_data.get("content") or "",
        )
        educations.append(education)

    links = []
    for link_data in parsed_data.get("links", []):
        if not link_data.get("name") or not link_data.get("url"):
            continue

        link = Link(
            name=link_data.get("name", ""),
            description=link_data.get("description") or "",
            url=link_data.get("url", ""),
        )
        links.append(link)

    return bio, skills, experiences, projects, stories, educations, links
