"""Resume generation logic."""

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


class ResumeGenerator:
    """Generate resumes using AI."""

    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialize resume generator.

        Args:
            provider: AI provider instance. If None, uses default from config.
        """
        self.provider = get_ai_provider()

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
        system_prompt = """You are a professional resume writer. Generate a well-formatted resume in markdown format.
The resume should be professional, concise, and highlight the candidate's strengths.
Use proper markdown formatting with headers, bullet points, and sections.
Do not use emojis or special characters in the resume output.
Do not use markdown divider syntax (---) between sections. Use blank lines for section separation.

Your work will be reviewed by two expert personas:
1. A literature degree holder who edits for brevity, spelling, word choice, and attention to detail. They ensure every word matters and that the details are perfect.
2. A business executive with a VP title or higher who edits for clarity and impact, highlighting achievements so they can be quickly and easily understood by busy decision-makers.

Incorporate the perspectives of both reviewers: ensure perfect spelling, precise word choice, and concise language while also making achievements clear, impactful, and easily scannable."""

        # Build content summary
        content_parts = []

        # Add bio information if available
        if bio:
            bio_info = f"## Candidate Information\n**Name:** {bio.name}"
            if bio.location:
                bio_info += f"\n**Location:** {bio.location}"
            content_parts.append(bio_info)

        if skills:
            content_parts.append("## Skills")
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
            content_parts.append("\n## Experience")
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

        content_text = "\n\n".join(content_parts)

        prompt = f"""Generate a professional resume based on the following information:

{content_text}

Create a well-structured resume in markdown format with the following sections in this exact order:
1. Header with name{" and location" if bio and bio.location else ""} and contact information
2. Links (place directly under the header/bio information without a "Links" heading - format them inline or as a simple list)
3. Summary/Objective
4. Professional Experience (most recent first)
5. Skills (organized by category if applicable)
6. Projects (if applicable)
7. Key Achievements/Stories
8. Education

{"Use the candidate's name and location from the Candidate Information section above in the header." if bio else ""}
Place links directly under the header/bio information without a "Links" heading. Format them inline or as a simple list.
Do not use markdown divider syntax (---) between sections. Use blank lines for section separation.

IMPORTANT FORMATTING REQUIREMENTS:
- Use heading 1 (#) for the candidate's name at the top
- Use heading 2 (##) for major section titles (e.g., "Professional Experience", "Skills", "Education")
- Use heading 3 (###) for subsection titles (e.g., individual job titles, project names, achievement titles)
- For the Skills section: Format each skill as a list item with the skill name in bold followed by a colon, then the description (e.g., "- **Skill Name**: Description")
- For Professional Experience: Format each experience with the job title as heading 3 (###), then on the next line include dates and location (e.g., "### Job Title\nDates | Location" or "### Job Title\nDates - Location")

Make it professional, concise, and impactful. Do not use emojis or special characters in the output."""

        try:
            resume = self.provider.generate(prompt, system_prompt)
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
        system_prompt = """You are a professional resume writer specializing in ATS-optimized resumes.
Generate a customized resume that matches the job description while only using the candidate's actual experience.
Highlight relevant skills, experiences, and achievements that align with the job requirements.
Use proper markdown formatting with headers, bullet points, and sections.
Do not use emojis or special characters in the resume output.
Do not use markdown divider syntax (---) between sections. Use blank lines for section separation.

Your work will be reviewed by two expert personas:
1. A literature degree holder who edits for brevity, spelling, word choice, and attention to detail. They ensure every word matters and that the details are perfect.
2. A business executive with a VP title or higher who edits for clarity and impact, highlighting achievements so they can be quickly and easily understood by busy decision-makers.

Incorporate the perspectives of both reviewers: ensure perfect spelling, precise word choice, and concise language while also making achievements clear, impactful, and easily scannable."""

        # Build job description summary
        job_info = f"""
Job Title: {job.title or job.name}
Location: {job.location or "Not specified"}
Requirements: {job.requirements or "Not specified"}
Pay: {job.pay or "Not specified"}

Full Job Description:
{job.content}
"""

        # Build candidate data (same as general resume)
        content_parts = []

        # Add bio information if available
        if bio:
            bio_info = f"## Candidate Information\n**Name:** {bio.name}"
            if bio.location:
                bio_info += f"\n**Location:** {bio.location}"
            content_parts.append(bio_info)

        if skills:
            content_parts.append("## Available Skills")
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
            content_parts.append("\n## Work Experience")
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

        candidate_data = "\n\n".join(content_parts)

        prompt = f"""Generate a customized resume for the following job application:

{job_info}

Based on the candidate's actual experience and skills:

{candidate_data}

IMPORTANT: Only use the candidate's actual skills, experiences, stories, and projects provided above.
Do not make up or invent any information.

Create a well-structured, ATS-optimized resume in markdown format with the following sections in this exact order:
1. Header with name{" and location" if bio and bio.location else ""} and contact information
2. Links (place directly under the header/bio information without a "Links" heading - format them inline or as a simple list)
3. Summary/Objective
4. Professional Experience (most recent first)
5. Skills (organized by category if applicable)
6. Projects (if applicable)
7. Key Achievements/Stories
8. Education

{"Use the candidate's name and location from the Candidate Information section above in the header." if bio else ""}
Place links directly under the header/bio information without a "Links" heading. Format them inline or as a simple list.
Do not use markdown divider syntax (---) between sections. Use blank lines for section separation.

IMPORTANT FORMATTING REQUIREMENTS:
- Use heading 1 (#) for the candidate's name at the top
- Use heading 2 (##) for major section titles (e.g., "Professional Experience", "Skills", "Education")
- Use heading 3 (###) for subsection titles (e.g., individual job titles, project names, achievement titles)
- For the Skills section: Format each skill as a list item with the skill name in bold followed by a colon, then the description (e.g., "- **Skill Name**: Description")
- For Professional Experience: Format each experience with the job title as heading 3 (###), then on the next line include dates and location (e.g., "### Job Title\nDates | Location" or "### Job Title\nDates - Location")

Make it compelling and tailored to this specific job while being truthful to the candidate's background.
Do not use emojis or special characters in the output."""

        try:
            resume = self.provider.generate(prompt, system_prompt)
            return resume
        except Exception as e:
            raise ResumeGenerationError(f"Failed to generate general resume: {e}") from e

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
        system_prompt = """You are a professional resume writer specializing in improving resumes based on feedback.
Update the resume to address the suggestions in the check report while maintaining accuracy and only using the candidate's actual experience.
Do not use emojis or special characters in the resume output."""

        prompt = f"""Update the following resume based on the check report suggestions:

Current Resume:
{current_resume}

Check Report with Suggestions:
{check_report}

Job Description:
{job.content}

Available Candidate Data:
- Skills: {", ".join([s.name for s in skills])}
- Experiences: {", ".join([e.title for e in experiences])}
- Projects: {", ".join([p.name for p in projects])}
- Stories: {", ".join([st.title for st in stories])}
- Education: {", ".join([edu.name for edu in educations])}

IMPORTANT: Only use the candidate's actual information. Do not invent anything.

Generate an improved resume that:
1. Addresses the suggestions from the check report
2. Better matches the job requirements
3. Maintains accuracy and truthfulness
4. Uses proper markdown formatting

Return the complete updated resume in markdown format. Do not use emojis or special characters in the output."""

        try:
            resume = self.provider.generate(prompt, system_prompt)
            return resume
        except Exception as e:
            raise ResumeGenerationError(f"Failed to generate general resume: {e}") from e

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
        system_prompt = """You are a professional cover letter writer. Generate a compelling, personalized cover letter in markdown format.
The cover letter should be professional, engaging, and tailored to the specific job application.
Use proper markdown formatting with paragraphs and appropriate structure.
Do not use emojis or special characters in the output.
The cover letter must be no more than 500 words.

Your work will be reviewed by two expert personas:
1. A literature degree holder who edits for brevity, spelling, word choice, and attention to detail. They ensure every word matters and that the details are perfect.
2. A business executive with a VP title or higher who edits for clarity and impact, highlighting achievements so they can be quickly and easily understood by busy decision-makers.

Incorporate the perspectives of both reviewers: ensure perfect spelling, precise word choice, and concise language while also making achievements clear, impactful, and easily scannable."""

        # Build job description summary
        job_info = f"""
Job Title: {job.title or job.name}
Location: {job.location or "Not specified"}
Requirements: {job.requirements or "Not specified"}
Pay: {job.pay or "Not specified"}

Full Job Description:
{job.content}
"""

        # Build candidate data
        content_parts = []

        # Add bio information if available
        if bio:
            bio_info = f"## Candidate Information\n**Name:** {bio.name}"
            if bio.location:
                bio_info += f"\n**Location:** {bio.location}"
            content_parts.append(bio_info)

        if skills:
            content_parts.append("## Available Skills")
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
            content_parts.append("\n## Work Experience")
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

        candidate_data = "\n\n".join(content_parts)

        # Build reason section if provided
        reason_section = ""
        if reason:
            reason_section = f"""

## Reason for Interest

{reason}
"""

        prompt = f"""Generate a personalized cover letter for the following job application:

{job_info}

Based on the candidate's actual experience and skills:

{candidate_data}
{reason_section}

IMPORTANT: Only use the candidate's actual skills, experiences, stories, and projects provided above.
Do not make up or invent any information.

Create a compelling, professional cover letter in markdown format that:
1. Addresses the specific job requirements and demonstrates how the candidate's background aligns
2. Highlights relevant skills, experiences, and achievements from the candidate's actual background
3. Shows enthusiasm and genuine interest in the position
4. Uses professional language and proper formatting
5. Includes appropriate greeting and closing
6. {"Incorporates the reason for interest provided above" if reason else ""}

{"Use the candidate's name from the Candidate Information section above in the signature." if bio else ""}
The cover letter must be NO MORE THAN 500 WORDS. Be concise and impactful.
Do not use emojis or special characters in the output."""

        try:
            cover_letter = self.provider.generate(prompt, system_prompt)
            return cover_letter
        except Exception as e:
            raise ResumeGenerationError(f"Failed to generate cover letter: {e}") from e
