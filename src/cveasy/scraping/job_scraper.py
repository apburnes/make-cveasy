"""Job description web scraper."""

import re
import requests
from bs4 import BeautifulSoup
from typing import Optional
from urllib.parse import urlparse

from cveasy.models.job import Job


class JobScraper:
    """Scrape job descriptions from URLs."""

    def __init__(self):
        """Initialize scraper with default headers."""
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def scrape(self, url: str) -> Optional[Job]:
        """
        Scrape job description from URL.

        Args:
            url: URL to scrape

        Returns:
            Job model with scraped data, or None if scraping fails
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Try to extract job information
            # This is a basic implementation - can be enhanced for specific job sites
            job_data = self._extract_job_data(soup, url)

            return job_data

        except Exception as e:
            print(f"Error scraping URL: {e}")
            return None

    def _extract_job_data(self, soup: BeautifulSoup, url: str) -> Job:
        """Extract job data from parsed HTML."""
        # Try to find job title
        title = self._find_title(soup)

        # Try to find location
        location = self._find_location(soup)

        # Try to find requirements
        requirements = self._find_requirements(soup)

        # Try to find pay/salary
        pay = self._find_pay(soup)

        # Get full description text
        description = self._find_description(soup)

        # Extract name from URL or title
        name = title or self._extract_name_from_url(url)

        return Job(
            name=name or "Job Application",
            title=title,
            location=location,
            requirements=requirements,
            pay=pay,
            content=description,
        )

    def _find_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Find job title in HTML."""
        # Common selectors for job titles
        selectors = [
            "h1",
            ".job-title",
            "[class*='title']",
            "[data-testid*='title']",
            "title",
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text and len(text) < 200:  # Reasonable title length
                    return text

        return None

    def _find_location(self, soup: BeautifulSoup) -> Optional[str]:
        """Find job location in HTML."""
        # Common selectors for location
        selectors = [
            "[class*='location']",
            "[data-testid*='location']",
            "[class*='address']",
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text:
                    return text

        # Try to find in text patterns
        text = soup.get_text()
        location_patterns = [
            r"Location:\s*(.+?)(?:\n|$)",
            r"Location\s*(.+?)(?:\n|$)",
        ]

        for pattern in location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

        return None

    def _find_requirements(self, soup: BeautifulSoup) -> Optional[str]:
        """Find job requirements in HTML."""
        # Common selectors for requirements
        selectors = [
            "[class*='requirement']",
            "[class*='qualification']",
            "[data-testid*='requirement']",
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text:
                    return text

        # Try to find in text patterns
        text = soup.get_text()
        requirement_patterns = [
            r"Requirements?:\s*(.+?)(?:\n\n|Qualifications?:)",
            r"Qualifications?:\s*(.+?)(?:\n\n|Requirements?:)",
        ]

        for pattern in requirement_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                return match.group(1).strip()[:500]  # Limit length

        return None

    def _find_pay(self, soup: BeautifulSoup) -> Optional[str]:
        """Find pay/salary information in HTML."""
        # Common selectors for pay
        selectors = [
            "[class*='salary']",
            "[class*='pay']",
            "[class*='compensation']",
            "[data-testid*='salary']",
        ]

        for selector in selectors:
            elements = soup.select(selector)
            for elem in elements:
                text = elem.get_text(strip=True)
                if text:
                    return text

        # Try to find in text patterns
        text = soup.get_text()
        pay_patterns = [
            r"\$[\d,]+(?:-\$?[\d,]+)?(?:\s*(?:per\s+)?(?:year|month|hour|yr|mo|hr))?",
            r"Salary:\s*(.+?)(?:\n|$)",
            r"Compensation:\s*(.+?)(?:\n|$)",
        ]

        for pattern in pay_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(0).strip()

        return None

    def _find_description(self, soup: BeautifulSoup) -> str:
        """Find full job description text."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "header", "footer"]):
            script.decompose()

        # Try to find main content area
        content_selectors = [
            "[class*='description']",
            "[class*='content']",
            "[class*='job-description']",
            "main",
            "article",
        ]

        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                return elements[0].get_text(separator="\n", strip=True)

        # Fallback to body text
        return soup.get_text(separator="\n", strip=True)

    def _extract_name_from_url(self, url: str) -> str:
        """Extract a name from URL path."""
        parsed = urlparse(url)
        path_parts = [p for p in parsed.path.split("/") if p]
        if path_parts:
            return path_parts[-1].replace("-", " ").title()
        return "Job Application"
