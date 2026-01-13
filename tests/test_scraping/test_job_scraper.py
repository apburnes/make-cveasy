"""Tests for job scraper."""

from unittest.mock import Mock, patch
from cveasy.scraping.job_scraper import JobScraper


def test_job_scraper_initialization():
    """Test job scraper initialization."""
    scraper = JobScraper()

    assert scraper.headers is not None
    assert "User-Agent" in scraper.headers


@patch("cveasy.scraping.job_scraper.requests.get")
def test_scrape_job_description(mock_get):
    """Test scraping job description."""
    # Mock response
    mock_response = Mock()
    mock_response.text = "<html><body><h1>Software Engineer</h1><p>Job description</p></body></html>"
    mock_response.raise_for_status = Mock()
    mock_get.return_value = mock_response

    scraper = JobScraper()
    job = scraper.scrape("https://example.com/job")

    assert job is not None
    assert job.name is not None
