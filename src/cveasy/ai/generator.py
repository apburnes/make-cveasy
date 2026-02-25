"""Resume generation logic."""

import logging
from typing import List, Optional
from cveasy.ai.providers import AIProvider, get_ai_provider
from cveasy.models.skill import Skill
from cveasy.models.experience import Experience
from cveasy.models.story import Story
from cveasy.models.link import Link
from cveasy.models.project import Project
from cveasy.models.job import Job
from cveasy.models.education import Education
from cveasy.models.bio import Bio
from cveasy.exceptions import ResumeGenerationError

logger = logging.getLogger(__name__)

EXPERT_REVIEW_INSTRUCTION = (
    "Your work will be reviewed by two expert personas:\n"
    "1. A literature degree holder who edits for brevity, spelling, word choice, "
    "and attention to detail. They ensure every word matters and that the details are perfect.\n"
    "2. A business executive with a VP title or higher who edits for clarity and impact, "
    "highlighting achievements so they can be quickly and easily understood by busy decision-makers.\n"
    "\n"
    "Incorporate the perspectives of both reviewers: ensure perfect spelling, precise word choice, "
    "and concise language while also making achievements clear, impactful, and easily scannable."
)

FORMATTING_REQUIREMENTS = (
    "IMPORTANT FORMATTING REQUIREMENTS:\n"
    "- Use heading 1 (#) for the candidate's name at the top\n"
    "- Use heading 2 (##) for major section titles "
    '(e.g., "Professional Experience", "Skills", "Education")\n'
    "- Use heading 3 (###) for subsection titles "
    "(e.g., individual job titles, project names, achievement titles)\n"
    "- For the Skills section: Format each skill as a list item with the skill name in bold "
    'followed by a colon, then the description (e.g., "- **Skill Name**: Description")\n'
    "- For Professional Experience: Format each experience with the job title as heading 3 (###), "
    "then on the next line include dates and location "
    '(e.g., "### Job Title\\nDates | Location" or "### Job Title\\nDates - Location")'
)

NO_SPECIAL_CHARS = "Do not use emojis or special characters in the resume output."
NO_DIVIDERS = (
    "Do not use markdown divider syntax (---) between sections. "
    "Use blank lines for section separation."
)


def _section_order(location_clause: str = "") -> str:
    return (
        "Create a well-structured resume in markdown format with the following sections "
        "in this exact order:\n"
        f"1. Header with name{location_clause} and contact information\n"
        "2. Links (place directly under the header/bio information without a "
        '"Links" heading - format them inline or as a simple list)\n'
        "3. Summary/Objective\n"
        "4. Professional Experience (most recent first)\n"
        "5. Skills (organized by category if applicable)\n"
        "6. Projects (if applicable)\n"
        "7. Key Achievements/Stories\n"
        "8. Education"
    )


class ResumeGenerator:
    """Generate resumes using AI."""

    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialize resume generator.

        Args:
            provider: AI provider instance. If None, uses default from config.
        """
        self.provider = provider or get_ai_provider()

    def _format_candidate_data(
        self,
        skills: List[Skill],
        experiences: List[Experience],
        stories: List[Story],
        links: List[Link],
        projects: List[Project],
        educations: List[Education],
        bio: Optional[Bio] = None,
        skills_heading: str = "## Skills",
        experience_heading: str = "\n## Experience",
    ) -> str:
        """
        Format candidate data into a text summary for AI prompts.

        Args:
            skills: List of skills
            experiences: List of experiences
            stories: List of stories
            links: List of links
            projects: List of projects
            educations: List of educations
            bio: Optional bio information (name and location)
            skills_heading: Heading for skills section
            experience_heading: Heading for experience section

        Returns:
            Formatted candidate data as a string
        """
        content_parts = []

        if bio:
            bio_info = f"## Candidate Information\n**Name:** {bio.name}"
            if bio.location:
                bio_info += f"\n**Location:** {bio.location}"
            content_parts.append(bio_info)

        if skills:
            content_parts.append(skills_heading)
            for skill in skills:
                skill_info = f"- **{skill.name}**"
                if skill.category:
                    skill_info += f" ({skill.category})"
                if skill.years:
                    skill_info += f" - {skill.years} years"
                if skill.proficiency:
                    skill_info += f" - {skill.proficiency}"
                if skill.content:
                    skill_info += f"\n  {skill.content}"
                content_parts.append(skill_info)

        if experiences:
            content_parts.append(experience_heading)
            for exp in experiences:
                exp_info = f"### {exp.title} at {exp.organization}"
                if exp.start_date and exp.end_date:
                    exp_info += f" ({exp.start_date} - {exp.end_date})"
                if exp.location:
                    exp_info += f" - {exp.location}"
                exp_info += f"\n{exp.content}"
                content_parts.append(exp_info)

        if projects:
            content_parts.append("\n## Projects")
            for proj in projects:
                proj_info = f"### {proj.name}"
                if proj.description:
                    proj_info += f"\n{proj.description}"
                if proj.link:
                    proj_info += f"\nLink: {proj.link}"
                if proj.content:
                    proj_info += f"\n{proj.content}"
                content_parts.append(proj_info)

        if stories:
            content_parts.append("\n## Key Achievements")
            for story in stories:
                story_info = f"### {story.title}"
                if story.context:
                    story_info += f"\nContext: {story.context}"
                if story.outcome:
                    story_info += f"\nOutcome: {story.outcome}"
                if story.content:
                    story_info += f"\n{story.content}"
                content_parts.append(story_info)

        if educations:
            content_parts.append("\n## Education")
            for edu in educations:
                edu_info = f"### {edu.name}"
                if edu.organization:
                    edu_info += f" - {edu.organization}"
                if edu.degree:
                    edu_info += f"\n{edu.degree}"
                if edu.certificate:
                    edu_info += f"\nCertificate: {edu.certificate}"
                if edu.start_date and edu.end_date:
                    edu_info += f"\n{edu.start_date} - {edu.end_date}"
                elif edu.start_date:
                    edu_info += f"\n{edu.start_date}"
                if edu.content:
                    edu_info += f"\n{edu.content}"
                content_parts.append(edu_info)

        if links:
            content_parts.append("\n## Links")
            for link in links:
                content_parts.append(f"- **{link.name}**: {link.url} - {link.description}")

        return "\n\n".join(content_parts)

    def generate_general_resume(
        self,
        skills: List[Skill],
        experiences: List[Experience],
        stories: List[Story],
        links: List[Link],
        projects: List[Project],
        educations: List[Education],
        bio: Optional[Bio] = None,
    ) -> str:
        """
        Generate a general resume from all available data.

        Args:
            skills: List of skills
            experiences: List of experiences
            stories: List of stories
            links: List of links
            projects: List of projects
            educations: List of educations
            bio: Optional bio information (name and location)

        Returns:
            Generated resume in markdown format
        """
        system_prompt = (
            "You are a professional resume writer. Generate a well-formatted resume in markdown format.\n"
            "The resume should be professional, concise, and highlight the candidate's strengths.\n"
            "Use proper markdown formatting with headers, bullet points, and sections.\n"
            f"{NO_SPECIAL_CHARS}\n{NO_DIVIDERS}\n\n{EXPERT_REVIEW_INSTRUCTION}"
        )

        content_text = self._format_candidate_data(
            skills,
            experiences,
            stories,
            links,
            projects,
            educations,
            bio,
        )

        location_clause = " and location" if bio and bio.location else ""
        bio_instruction = (
            "Use the candidate's name and location from the Candidate Information "
            "section above in the header.\n"
            if bio
            else ""
        )

        prompt = (
            f"Generate a professional resume based on the following information:\n\n"
            f"{content_text}\n\n"
            f"{_section_order(location_clause)}\n\n"
            f"{bio_instruction}"
            f"Place links directly under the header/bio information without a "
            f'"Links" heading. Format them inline or as a simple list.\n'
            f"{NO_DIVIDERS}\n\n"
            f"{FORMATTING_REQUIREMENTS}\n\n"
            f"Make it professional, concise, and impactful. {NO_SPECIAL_CHARS}"
        )

        try:
            logger.debug("Generating general resume (prompt: %d chars)", len(prompt))
            resume = self.provider.generate(prompt, system_prompt)
            logger.debug("General resume generated (%d chars)", len(resume))
            return resume
        except Exception as e:
            raise ResumeGenerationError(f"Failed to generate general resume: {e}") from e

    def generate_customized_resume(
        self,
        job: Job,
        skills: List[Skill],
        experiences: List[Experience],
        stories: List[Story],
        links: List[Link],
        projects: List[Project],
        educations: List[Education],
        bio: Optional[Bio] = None,
    ) -> str:
        """
        Generate a customized resume for a specific job application.

        Args:
            job: Job application details
            skills: List of skills
            experiences: List of experiences
            stories: List of stories
            links: List of links
            projects: List of projects
            educations: List of educations
            bio: Optional bio information (name and location)

        Returns:
            Generated resume in markdown format
        """
        system_prompt = (
            "You are a professional resume writer specializing in ATS-optimized resumes.\n"
            "Generate a customized resume that matches the job description while only using "
            "the candidate's actual experience.\n"
            "Highlight relevant skills, experiences, and achievements that align with the "
            "job requirements.\n"
            "Use proper markdown formatting with headers, bullet points, and sections.\n"
            f"{NO_SPECIAL_CHARS}\n{NO_DIVIDERS}\n\n{EXPERT_REVIEW_INSTRUCTION}"
        )

        job_info = (
            f"Job Title: {job.title or job.name}\n"
            f"Location: {job.location or 'Not specified'}\n"
            f"Requirements: {job.requirements or 'Not specified'}\n"
            f"Pay: {job.pay or 'Not specified'}\n\n"
            f"Full Job Description:\n{job.content}"
        )

        candidate_data = self._format_candidate_data(
            skills,
            experiences,
            stories,
            links,
            projects,
            educations,
            bio,
            skills_heading="## Available Skills",
            experience_heading="\n## Work Experience",
        )

        location_clause = " and location" if bio and bio.location else ""
        bio_instruction = (
            "Use the candidate's name and location from the Candidate Information "
            "section above in the header.\n"
            if bio
            else ""
        )

        prompt = (
            f"Generate a customized resume for the following job application:\n\n"
            f"{job_info}\n\n"
            f"Based on the candidate's actual experience and skills:\n\n"
            f"{candidate_data}\n\n"
            f"IMPORTANT: Only use the candidate's actual skills, experiences, stories, "
            f"and projects provided above.\nDo not make up or invent any information.\n\n"
            f"{_section_order(location_clause)}\n\n"
            f"{bio_instruction}"
            f"Place links directly under the header/bio information without a "
            f'"Links" heading. Format them inline or as a simple list.\n'
            f"{NO_DIVIDERS}\n\n"
            f"{FORMATTING_REQUIREMENTS}\n\n"
            f"Make it compelling and tailored to this specific job while being truthful "
            f"to the candidate's background.\n{NO_SPECIAL_CHARS}"
        )

        try:
            logger.debug("Generating customized resume (prompt: %d chars)", len(prompt))
            resume = self.provider.generate(prompt, system_prompt)
            logger.debug("Customized resume generated (%d chars)", len(resume))
            return resume
        except Exception as e:
            raise ResumeGenerationError(f"Failed to generate customized resume: {e}") from e

    def update_resume_from_check_report(
        self,
        current_resume: str,
        check_report: str,
        job: Job,
        skills: List[Skill],
        experiences: List[Experience],
        stories: List[Story],
        links: List[Link],
        projects: List[Project],
        educations: List[Education],
        bio: Optional[Bio] = None,
    ) -> str:
        """
        Update resume based on check report suggestions.

        Args:
            current_resume: Current resume content
            check_report: Check report with suggestions
            job: Job application details
            skills: List of skills
            experiences: List of experiences
            stories: List of stories
            links: List of links
            projects: List of projects
            educations: List of educations
            bio: Optional bio information (name and location)

        Returns:
            Updated resume in markdown format
        """
        system_prompt = (
            "You are a professional resume writer specializing in improving resumes "
            "based on feedback.\n"
            "Update the resume to address the suggestions in the check report while "
            "maintaining accuracy and only using the candidate's actual experience.\n"
            f"{NO_SPECIAL_CHARS}"
        )

        prompt = (
            f"Update the following resume based on the check report suggestions:\n\n"
            f"Current Resume:\n{current_resume}\n\n"
            f"Check Report with Suggestions:\n{check_report}\n\n"
            f"Job Description:\n{job.content}\n\n"
            f"Available Candidate Data:\n"
            f"- Skills: {', '.join([s.name for s in skills])}\n"
            f"- Experiences: {', '.join([e.title for e in experiences])}\n"
            f"- Projects: {', '.join([p.name for p in projects])}\n"
            f"- Stories: {', '.join([st.title for st in stories])}\n"
            f"- Education: {', '.join([edu.name for edu in educations])}\n\n"
            f"IMPORTANT: Only use the candidate's actual information. Do not invent anything.\n\n"
            f"Generate an improved resume that:\n"
            f"1. Addresses the suggestions from the check report\n"
            f"2. Better matches the job requirements\n"
            f"3. Maintains accuracy and truthfulness\n"
            f"4. Uses proper markdown formatting\n\n"
            f"Return the complete updated resume in markdown format. {NO_SPECIAL_CHARS}"
        )

        try:
            logger.debug("Updating resume from check report (prompt: %d chars)", len(prompt))
            resume = self.provider.generate(prompt, system_prompt)
            logger.debug("Resume updated from check report (%d chars)", len(resume))
            return resume
        except Exception as e:
            raise ResumeGenerationError(f"Failed to update resume from check report: {e}") from e

    def generate_cover_letter(
        self,
        job: Job,
        skills: List[Skill],
        experiences: List[Experience],
        stories: List[Story],
        links: List[Link],
        projects: List[Project],
        educations: List[Education],
        bio: Optional[Bio] = None,
        reason: Optional[str] = None,
    ) -> str:
        """
        Generate a personalized cover letter for a specific job application.

        Args:
            job: Job application details
            skills: List of skills
            experiences: List of experiences
            stories: List of stories
            links: List of links
            projects: List of projects
            educations: List of educations
            bio: Optional bio information (name and location)
            reason: Optional reason for interest in the job

        Returns:
            Generated cover letter in markdown format (maximum 500 words)
        """
        system_prompt = (
            "You are a professional cover letter writer. Generate a compelling, "
            "personalized cover letter in markdown format.\n"
            "The cover letter should be professional, engaging, and tailored to the "
            "specific job application.\n"
            "Use proper markdown formatting with paragraphs and appropriate structure.\n"
            "Do not use emojis or special characters in the output.\n"
            "The cover letter must be no more than 500 words.\n\n"
            f"{EXPERT_REVIEW_INSTRUCTION}"
        )

        job_info = (
            f"Job Title: {job.title or job.name}\n"
            f"Location: {job.location or 'Not specified'}\n"
            f"Requirements: {job.requirements or 'Not specified'}\n"
            f"Pay: {job.pay or 'Not specified'}\n\n"
            f"Full Job Description:\n{job.content}"
        )

        candidate_data = self._format_candidate_data(
            skills,
            experiences,
            stories,
            links,
            projects,
            educations,
            bio,
            skills_heading="## Available Skills",
            experience_heading="\n## Work Experience",
        )

        reason_section = ""
        if reason:
            reason_section = f"\n\n## Reason for Interest\n\n{reason}\n"

        reason_instruction = "Incorporates the reason for interest provided above" if reason else ""
        bio_instruction = (
            "Use the candidate's name from the Candidate Information section above "
            "in the signature.\n"
            if bio
            else ""
        )

        prompt = (
            f"Generate a personalized cover letter for the following job application:\n\n"
            f"{job_info}\n\n"
            f"Based on the candidate's actual experience and skills:\n\n"
            f"{candidate_data}"
            f"{reason_section}\n\n"
            f"IMPORTANT: Only use the candidate's actual skills, experiences, stories, "
            f"and projects provided above.\nDo not make up or invent any information.\n\n"
            f"Create a compelling, professional cover letter in markdown format that:\n"
            f"1. Addresses the specific job requirements and demonstrates how the "
            f"candidate's background aligns\n"
            f"2. Highlights relevant skills, experiences, and achievements from the "
            f"candidate's actual background\n"
            f"3. Shows enthusiasm and genuine interest in the position\n"
            f"4. Uses professional language and proper formatting\n"
            f"5. Includes appropriate greeting and closing\n"
            f"6. {reason_instruction}\n\n"
            f"{bio_instruction}"
            f"The cover letter must be NO MORE THAN 500 WORDS. Be concise and impactful.\n"
            f"Do not use emojis or special characters in the output."
        )

        try:
            logger.debug("Generating cover letter (prompt: %d chars)", len(prompt))
            cover_letter = self.provider.generate(prompt, system_prompt)
            logger.debug("Cover letter generated (%d chars)", len(cover_letter))
            return cover_letter
        except Exception as e:
            raise ResumeGenerationError(f"Failed to generate cover letter: {e}") from e
