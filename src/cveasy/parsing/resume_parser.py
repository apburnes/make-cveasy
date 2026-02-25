"""Resume parser for extracting structured data from PDF/DOCX files."""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
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
        extracted_links = []
        for page in reader.pages:
            text_parts.append(page.extract_text())
            # Extract link annotations from PDF
            if page.annotations:
                for annotation in page.annotations:
                    ann_obj = annotation.get_object()
                    if ann_obj.get("/Subtype") == "/Link":
                        action = ann_obj.get("/A")
                        if action and action.get("/URI"):
                            uri = str(action["/URI"])
                            if uri not in extracted_links:
                                extracted_links.append(uri)
        text = "\n".join(text_parts)
        if extracted_links:
            text += "\n\nExtracted Links:"
            for link_url in extracted_links:
                text += f"\n- {link_url}"
        return text
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
        extracted_links = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)
            # Extract hyperlinks from DOCX XML
            for element in paragraph._element:
                if element.tag.endswith("}hyperlink"):
                    r_id = element.get(
                        "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
                    )
                    if r_id and r_id in doc.part.rels:
                        url = doc.part.rels[r_id].target_ref
                        # Get display text from runs inside the hyperlink
                        label_parts = []
                        for run in element:
                            if run.text:
                                label_parts.append(run.text)
                        label = "".join(label_parts) or url
                        link_entry = f"{label}: {url}"
                        if link_entry not in extracted_links:
                            extracted_links.append(link_entry)
        text = "\n".join(text_parts)
        if extracted_links:
            text += "\n\nExtracted Links:"
            for link_entry in extracted_links:
                text += f"\n- {link_entry}"
        return text
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
      "related_experiences": ["Job title 1", "Job title 2"]
    }}
  ],
  "experiences": [
    {{
      "title": "Job title",
      "organization": "Company name",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or 'Present'",
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
      "content": "Detailed project description",
      "related_experiences": ["Job title 1"]
    }}
  ],
  "stories": [
    {{
      "title": "Achievement/story title",
      "context": "Context or situation",
      "outcome": "Result or outcome",
      "content": "Detailed description",
      "related_experiences": ["Job title 1"]
    }}
  ],
  "education": [
    {{
      "name": "Education name/title",
      "start_date": "YYYY-MM",
      "end_date": "YYYY-MM or 'Present'",
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
      "url": "The actual URL/href (e.g., https://linkedin.com/in/username)"
    }}
  ]
}}

IMPORTANT: For relationships:
- In "experiences", include "related_skills" (array of skill names used in this role) and "related_stories" (array of story/achievement titles from this role)
- In "skills", include "related_experiences" (array of job titles where this skill was used)
- In "stories", include "related_experiences" (array of job titles where this story/achievement occurred)
- In "projects", include "related_experiences" (array of job titles where this project was worked on)
- Use the exact names/titles as they appear in the respective arrays (e.g., if a skill is named "Python", reference it as "Python" in related_skills)
- If no relationships exist, use an empty array []
- For links, extract the actual URL/href, NOT the display text. If the resume text contains an "Extracted Links" section, use the actual URLs from there rather than display text

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


def _normalize_name(name: str) -> str:
    """Produce a canonical form for fuzzy name matching.

    1. Strip + lowercase
    2. Remove parentheses but keep their content
    3. Remove '.' and '/'
    4. Collapse whitespace
    5. Preserve '+' and '#' (for C++, C#)
    """
    s = name.strip().lower()
    s = re.sub(r"[()]", " ", s)
    s = s.replace(".", "").replace("/", "")
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _extract_aliases(name: str) -> List[str]:
    """Return additional normalized lookup keys from a name.

    - Parenthetical content: "Amazon Web Services (AWS)" -> ["aws", "amazon web services"]
    - Acronym from 3+ word names: "Amazon Web Services" -> ["aws"]
    - Returns [] for simple single-word names
    """
    aliases: List[str] = []
    # Extract parenthetical content
    paren_match = re.search(r"\(([^)]+)\)", name)
    if paren_match:
        inner = paren_match.group(1).strip()
        aliases.append(_normalize_name(inner))
        # Also add the name without parenthetical
        outside = re.sub(r"\([^)]*\)", "", name).strip()
        if outside:
            aliases.append(_normalize_name(outside))

    # Build acronym from 3+ word names (ignoring parenthetical)
    base = re.sub(r"\([^)]*\)", "", name).strip()
    words = base.split()
    if len(words) >= 3:
        acronym = "".join(w[0] for w in words if w).lower()
        if acronym not in aliases:
            aliases.append(acronym)

    return aliases


def _build_name_lookup(items: List, name_attr: str) -> Dict[str, object]:
    """Build a multi-key lookup dict mapping various name forms to model objects.

    For each item, registers: original name, lowercased name, normalized name,
    and all normalized aliases.
    """
    lookup: Dict[str, object] = {}
    for item in items:
        name = getattr(item, name_attr)
        # Original name (exact)
        if name not in lookup:
            lookup[name] = item
        # Lowercased
        lower = name.lower()
        if lower not in lookup:
            lookup[lower] = item
        # Normalized
        normalized = _normalize_name(name)
        if normalized not in lookup:
            lookup[normalized] = item
        # Aliases
        for alias in _extract_aliases(name):
            if alias not in lookup:
                lookup[alias] = item
    return lookup


def _resolve_name(name: str, lookup: Dict[str, object]) -> Optional[object]:
    """Multi-strategy name resolution. Stops at first match.

    1. Exact -> 2. Lowercase -> 3. Normalized -> 4. Normalized aliases of input
    """
    # 1. Exact
    obj = lookup.get(name)
    if obj:
        logger.debug("Matched '%s' via exact", name)
        return obj
    # 2. Lowercase
    obj = lookup.get(name.lower())
    if obj:
        logger.debug("Matched '%s' via lowercase", name)
        return obj
    # 3. Normalized
    normalized = _normalize_name(name)
    obj = lookup.get(normalized)
    if obj:
        logger.debug("Matched '%s' via normalized", name)
        return obj
    # 4. Normalized aliases of input
    for alias in _extract_aliases(name):
        obj = lookup.get(alias)
        if obj:
            logger.debug("Matched '%s' via alias '%s'", name, alias)
            return obj
    return None


# Known short technical names that are safe for content scanning
_KNOWN_SHORT_NAMES = frozenset(
    {
        "C",
        "R",
        "Go",
        "AI",
        "ML",
        "DL",
        "CI",
        "CD",
        "DB",
        "UI",
        "UX",
        "QA",
        "JS",
        "TS",
        "VB",
        "OS",
    }
)


def _find_skills_in_content(
    content: str, skills: List[Skill], already_matched_slugs: Set[str]
) -> List[Skill]:
    """Scan experience content text for skill name mentions.

    Returns skills found in content that aren't already matched.
    Short name handling:
    - Names >= 3 chars: case-insensitive word-boundary regex
    - Names 1-2 chars: case-sensitive with stricter boundaries, only known tech names
    """
    matched: List[Skill] = []
    if not content:
        return matched

    for skill in skills:
        if skill.slug in already_matched_slugs:
            continue

        name = skill.name.strip()
        if not name:
            continue

        if len(name) <= 2:
            # Only match known short technical names
            if name not in _KNOWN_SHORT_NAMES:
                continue
            if name == "C":
                # Avoid matching inside C++ or C#
                pattern = r"(?<![a-zA-Z])C(?![a-zA-Z+#])"
            elif name == "Go":
                pattern = r"(?<![a-zA-Z])Go(?:lang)?(?![a-zA-Z])"
            elif name == "R":
                pattern = r"(?<![a-zA-Z])R(?![a-zA-Z])"
            else:
                # Generic short name: case-sensitive, word-boundary-like
                escaped = re.escape(name)
                pattern = rf"(?<![a-zA-Z]){escaped}(?![a-zA-Z])"
            if re.search(pattern, content):
                matched.append(skill)
        else:
            # >= 3 chars: case-insensitive word boundary
            escaped = re.escape(name)
            pattern = rf"\b{escaped}\b"
            if re.search(pattern, content, re.IGNORECASE):
                matched.append(skill)

    return matched


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
            related_experiences=[],
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

    # Step 3: Build lookup dictionaries for fuzzy name resolution
    skill_lookup = _build_name_lookup(skills, name_attr="name")
    experience_lookup = _build_name_lookup(experiences, name_attr="title")
    story_lookup = _build_name_lookup(stories, name_attr="title")
    project_lookup = _build_name_lookup(projects, name_attr="name")

    # Step 4: Process relationships from parsed data using fuzzy matching
    llm_link_count = 0

    # Process experiences -> skills and experiences -> stories
    for exp_data in parsed_data.get("experiences", []):
        if not exp_data.get("title") or not exp_data.get("organization"):
            continue

        exp_title = exp_data.get("title", "")
        experience = _resolve_name(exp_title, experience_lookup)
        if not experience:
            continue

        # Map related_skills names to skill slugs
        related_skill_names = exp_data.get("related_skills", [])
        if related_skill_names:
            for skill_name in related_skill_names:
                skill_obj = _resolve_name(skill_name, skill_lookup)
                if skill_obj and skill_obj.slug not in experience.related_skills:
                    experience.related_skills.append(skill_obj.slug)
                    llm_link_count += 1
                    # Set reverse relationship: skill -> experience
                    if experience.slug not in skill_obj.related_experiences:
                        skill_obj.related_experiences.append(experience.slug)
                elif not skill_obj:
                    logger.warning(
                        "Could not match skill name '%s' from experience '%s'",
                        skill_name,
                        exp_title,
                    )

        # Map related_stories titles to story slugs
        related_story_titles = exp_data.get("related_stories", [])
        if related_story_titles:
            for story_title in related_story_titles:
                story_obj = _resolve_name(story_title, story_lookup)
                if story_obj and story_obj.slug not in experience.related_stories:
                    experience.related_stories.append(story_obj.slug)
                    # Set reverse relationship: story -> experience
                    if experience.slug not in story_obj.related_experiences:
                        story_obj.related_experiences.append(experience.slug)

    # Process skills -> experiences
    for skill_data in parsed_data.get("skills", []):
        if not skill_data.get("name"):
            continue

        skill_name = skill_data.get("name", "")
        skill = _resolve_name(skill_name, skill_lookup)
        if not skill:
            continue

        # Map related_experiences titles to experience slugs
        related_exp_titles = skill_data.get(
            "related_experiences", skill_data.get("related_experience", [])
        )
        if related_exp_titles:
            for exp_title in related_exp_titles:
                exp_obj = _resolve_name(exp_title, experience_lookup)
                if exp_obj and exp_obj.slug not in skill.related_experiences:
                    skill.related_experiences.append(exp_obj.slug)
                    llm_link_count += 1

    # Process stories -> experiences (from parsed data)
    for story_data in parsed_data.get("stories", []):
        if not story_data.get("title"):
            continue
        story_title = story_data.get("title", "")
        story_obj = _resolve_name(story_title, story_lookup)
        if not story_obj:
            continue
        related_exp_titles = story_data.get("related_experiences", [])
        if related_exp_titles:
            for exp_title in related_exp_titles:
                exp_obj = _resolve_name(exp_title, experience_lookup)
                if exp_obj and exp_obj.slug not in story_obj.related_experiences:
                    story_obj.related_experiences.append(exp_obj.slug)

    # Process projects -> experiences (from parsed data)
    for proj_data in parsed_data.get("projects", []):
        if not proj_data.get("name"):
            continue
        proj_name = proj_data.get("name", "")
        proj_obj = _resolve_name(proj_name, project_lookup)
        if not proj_obj:
            continue
        related_exp_titles = proj_data.get("related_experiences", [])
        if related_exp_titles:
            for exp_title in related_exp_titles:
                exp_obj = _resolve_name(exp_title, experience_lookup)
                if exp_obj and exp_obj.slug not in proj_obj.related_experiences:
                    proj_obj.related_experiences.append(exp_obj.slug)

    # Step 5: Content-based fallback — scan experience content for skill mentions
    content_link_count = 0
    for experience in experiences:
        matched_slugs = set(experience.related_skills)
        content_matches = _find_skills_in_content(experience.content, skills, matched_slugs)
        for skill in content_matches:
            if skill.slug not in experience.related_skills:
                experience.related_skills.append(skill.slug)
                content_link_count += 1
                logger.info(
                    "Content scan: linked skill '%s' to experience '%s'",
                    skill.name,
                    experience.title,
                )
            if experience.slug not in skill.related_experiences:
                skill.related_experiences.append(experience.slug)

    total_links = llm_link_count + content_link_count
    logger.info(
        "Relationship matching: %d experience-skill links (%d from LLM, %d from content scan)",
        total_links,
        llm_link_count,
        content_link_count,
    )

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
