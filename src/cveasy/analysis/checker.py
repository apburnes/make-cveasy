"""Resume quality checker with LLM comparison."""

from typing import Dict, Optional
from cveasy.analysis.matcher import KeywordMatcher, SkillsMatcher
from cveasy.ai.providers import AIProvider, get_ai_provider
from cveasy.config import get_spacy_model
from cveasy.models.job import Job
from cveasy.models.skill import Skill


class ResumeChecker:
    """Check resume quality against job description."""

    def __init__(self, provider: Optional[AIProvider] = None):
        """
        Initialize resume checker.

        Args:
            provider: AI provider instance. If None, uses default from config.
        """
        self.provider = provider or get_ai_provider()
        model_name = get_spacy_model()
        self.keyword_matcher = KeywordMatcher(model_name=model_name)
        self.skills_matcher = SkillsMatcher(model_name=model_name)

    def check(
        self,
        resume_text: str,
        job: Job,
        skills: list[Skill],
    ) -> str:
        """
        Check resume against job description and generate report.

        Args:
            resume_text: Resume content
            job: Job application details
            skills: List of skills from resume data

        Returns:
            Markdown report with scores and suggestions
        """
        # Run keyword matching
        keyword_results = self.keyword_matcher.match_keywords(resume_text, job.content)

        # Run skills matching
        skill_names = [skill.name for skill in skills]
        skills_results = self.skills_matcher.match_skills(resume_text, job.content, skill_names)

        # Get LLM analysis
        llm_analysis = self._get_llm_analysis(resume_text, job)

        # Generate report
        report = self._generate_report(keyword_results, skills_results, llm_analysis, job)

        return report

    def _get_llm_analysis(self, resume_text: str, job: Job) -> Dict[str, str]:
        """
        Get LLM-based analysis of resume fit.

        Args:
            resume_text: Resume content
            job: Job application details

        Returns:
            Dictionary with analysis results
        """
        system_prompt = """You are a professional resume reviewer and career coach.
Analyze how well a resume matches a job description and provide specific, actionable feedback."""

        prompt = f"""Analyze how well this resume matches the job description:

Job Title: {job.title or job.name}
Job Description:
{job.content}

Resume:
{resume_text}

Provide:
1. Overall fit score (0-100) and brief explanation
2. Top 3 strengths that align with the job
3. Top 3 areas for improvement
4. Specific suggestions for better alignment (be specific and actionable)
5. Missing keywords or skills that should be emphasized
6. Recommendations for resume enhancement

Format your response clearly with sections."""

        analysis_text = self.provider.generate(prompt, system_prompt)

        return {
            "analysis": analysis_text,
        }

    def _generate_report(
        self,
        keyword_results: Dict,
        skills_results: Dict,
        llm_analysis: Dict,
        job: Job,
    ) -> str:
        """
        Generate markdown report from analysis results.

        Args:
            keyword_results: Keyword matching results
            skills_results: Skills matching results
            llm_analysis: LLM analysis results
            job: Job application details

        Returns:
            Markdown report
        """
        report_lines = [
            "# Resume Quality Check Report",
            "",
            f"**Job Application:** {job.name}",
            f"**Job Title:** {job.title or 'Not specified'}",
            f"**Date:** {job.created.strftime('%Y-%m-%d') if job.created else 'N/A'}",
            "",
            "---",
            "",
            "## Quantitative Metrics",
            "",
            "### Keyword Matching",
            f"- **Match Score:** {keyword_results['match_score']:.1f}%",
            f"- **Matched Keywords:** {keyword_results['matched_count']} / {keyword_results['total_job_keywords']}",
            f"- **Missing Keywords:** {keyword_results['missing_count']}",
            "",
            "### Skills Matching",
            f"- **Match Score:** {skills_results['match_score']:.1f}%",
            f"- **Matched Skills:** {skills_results['matched_count']} / {skills_results['total_job_skills']}",
            f"- **Missing Skills:** {skills_results['missing_count']}",
            "",
            "---",
            "",
            "## Detailed Analysis",
            "",
            llm_analysis["analysis"],
            "",
            "---",
            "",
            "## Missing Keywords",
            "",
        ]

        if keyword_results["missing_keywords"]:
            # Show top 20 missing keywords
            missing = keyword_results["missing_keywords"][:20]
            for keyword in missing:
                report_lines.append(f"- {keyword}")
            if len(keyword_results["missing_keywords"]) > 20:
                report_lines.append(
                    f"\n*... and {len(keyword_results['missing_keywords']) - 20} more*"
                )
        else:
            report_lines.append("No missing keywords found.")

        report_lines.extend(
            [
                "",
                "## Missing Skills",
                "",
            ]
        )

        if skills_results["missing_skills"]:
            for skill in skills_results["missing_skills"]:
                report_lines.append(f"- {skill}")
        else:
            report_lines.append("No missing skills found.")

        report_lines.extend(
            [
                "",
                "## Matching Keywords",
                "",
            ]
        )

        if keyword_results["matching_keywords"]:
            # Show top 20 matching keywords
            matching = keyword_results["matching_keywords"][:20]
            for keyword in matching:
                report_lines.append(f"- {keyword}")
            if len(keyword_results["matching_keywords"]) > 20:
                report_lines.append(
                    f"\n*... and {len(keyword_results['matching_keywords']) - 20} more*"
                )
        else:
            report_lines.append("No matching keywords found.")

        report_lines.extend(
            [
                "",
                "## Matching Skills",
                "",
            ]
        )

        if skills_results["matching_skills"]:
            for skill in skills_results["matching_skills"]:
                report_lines.append(f"- {skill}")
        else:
            report_lines.append("No matching skills found.")

        report_lines.append("")

        return "\n".join(report_lines)
