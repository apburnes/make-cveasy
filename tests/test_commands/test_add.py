"""Tests for add command."""

from unittest.mock import patch, MagicMock
from typer.testing import CliRunner

from cveasy.cli import app


def test_add_education_command(temp_dir):
    """Test adding an education entry."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(
            app, ["add", "education", "--name", "Bachelor of Science in Computer Science"]
        )

        assert result.exit_code == 0
        assert "Created education" in result.stdout

        # Check that file was created (with slug hash)
        education_dir = temp_dir / "education"
        education_files = list(education_dir.glob("bachelor-of-science-in-computer-science-*.md"))
        assert len(education_files) == 1


def test_add_education_with_all_flags(temp_dir):
    """Test adding an education entry with all optional flags."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(
            app,
            [
                "add",
                "education",
                "--name",
                "Master of Science",
                "--start_date",
                "2020-09-01",
                "--end_date",
                "2022-05-15",
                "--degree",
                "Master of Science",
                "--certificate",
                "Data Science Certificate",
                "--organization",
                "University Name",
            ],
        )

        assert result.exit_code == 0
        assert "Created education" in result.stdout

        # Check that file was created (with slug hash)
        education_dir = temp_dir / "education"
        education_files = list(education_dir.glob("master-of-science-*.md"))
        assert len(education_files) == 1

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        education = storage.load_education("Master of Science")
        assert education is not None
        assert education.name == "Master of Science"
        assert education.start_date == "2020-09"
        assert education.end_date == "2022-05"
        assert education.degree == "Master of Science"
        assert education.certificate == "Data Science Certificate"
        assert education.organization == "University Name"


def test_add_education_with_partial_flags(temp_dir):
    """Test adding an education entry with some optional flags."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(
            app,
            [
                "add",
                "education",
                "--name",
                "Certificate Program",
                "--certificate",
                "AWS Solutions Architect",
                "--organization",
                "AWS Training",
            ],
        )

        assert result.exit_code == 0
        assert "Created education" in result.stdout

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        education = storage.load_education("Certificate Program")
        assert education is not None
        assert education.name == "Certificate Program"
        assert education.certificate == "AWS Solutions Architect"
        assert education.organization == "AWS Training"
        assert education.degree is None
        assert education.start_date is None


def test_add_bio_command(temp_dir):
    """Test adding a bio with name only."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["add", "bio", "--name", "John Doe"])

        assert result.exit_code == 0
        assert "Created/updated bio" in result.stdout

        # Check that file was created
        bio_file = temp_dir / "bio.md"
        assert bio_file.exists()

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        bio = storage.load_bio()
        assert bio is not None
        assert bio.name == "John Doe"
        assert bio.location == ""  # Location defaults to empty string

        # Verify the file contains location attribute
        import frontmatter

        with open(bio_file, "r", encoding="utf-8") as f:
            post = frontmatter.load(f)
            assert "location" in post.metadata
            assert post.metadata["location"] == ""


def test_add_bio_command_with_location(temp_dir):
    """Test adding a bio with name and location."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(
            app,
            [
                "add",
                "bio",
                "--name",
                "John Doe",
                "--location",
                "San Francisco, CA",
            ],
        )

        assert result.exit_code == 0
        assert "Created/updated bio" in result.stdout

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        bio = storage.load_bio()
        assert bio is not None
        assert bio.name == "John Doe"
        assert bio.location == "San Francisco, CA"


def test_add_skill_command(temp_dir):
    """Test adding a skill."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["add", "skill", "--name", "Python"])

        assert result.exit_code == 0
        assert "Created skill" in result.stdout

        # Check that file was created (with slug hash)
        skills_dir = temp_dir / "skills"
        skill_files = list(skills_dir.glob("python-*.md"))
        assert len(skill_files) == 1

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        skill = storage.load_skill("Python")
        assert skill is not None
        assert skill.name == "Python"
        assert skill.category is None
        assert skill.content == ""


def test_add_experience_command(temp_dir):
    """Test adding an experience."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["add", "experience", "--name", "Senior Software Engineer"])

        assert result.exit_code == 0
        assert "Created experience" in result.stdout

        # Check that file was created (with slug hash)
        experiences_dir = temp_dir / "experiences"
        experience_files = list(experiences_dir.glob("senior-software-engineer-*.md"))
        assert len(experience_files) == 1

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        experience = storage.load_experience("Senior Software Engineer")
        assert experience is not None
        assert experience.title == "Senior Software Engineer"
        assert experience.organization == ""
        assert experience.content == ""


def test_add_story_command(temp_dir):
    """Test adding a story."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["add", "story", "--name", "Led Migration to Microservices"])

        assert result.exit_code == 0
        assert "Created story" in result.stdout

        # Check that file was created (with slug hash)
        stories_dir = temp_dir / "stories"
        story_files = list(stories_dir.glob("led-migration-to-microservices-*.md"))
        assert len(story_files) == 1

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        story = storage.load_story("Led Migration to Microservices")
        assert story is not None
        assert story.title == "Led Migration to Microservices"
        assert story.context is None
        assert story.content == ""


def test_add_link_command(temp_dir):
    """Test adding a link."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(
            app,
            [
                "add",
                "link",
                "--name",
                "LinkedIn",
                "--description",
                "Professional profile",
                "--url",
                "https://linkedin.com/in/username",
            ],
        )

        assert result.exit_code == 0
        assert "Created link" in result.stdout

        # Check that file was created (with slug hash)
        links_dir = temp_dir / "links"
        link_files = list(links_dir.glob("linkedin-*.md"))
        assert len(link_files) == 1

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        link = storage.load_link("LinkedIn")
        assert link is not None
        assert link.name == "LinkedIn"
        assert link.description == "Professional profile"
        assert link.url == "https://linkedin.com/in/username"


def test_add_project_command(temp_dir):
    """Test adding a project."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(
            app,
            [
                "add",
                "project",
                "--name",
                "E-commerce Platform",
                "--description",
                "Full-stack application",
            ],
        )

        assert result.exit_code == 0
        assert "Created project" in result.stdout

        # Check that file was created (with slug hash)
        projects_dir = temp_dir / "projects"
        project_files = list(projects_dir.glob("e-commerce-platform-*.md"))
        assert len(project_files) == 1

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        project = storage.load_project("E-commerce Platform")
        assert project is not None
        assert project.name == "E-commerce Platform"
        assert project.description == "Full-stack application"
        assert project.link is None
        assert project.content == ""


def test_add_project_command_with_link(temp_dir):
    """Test adding a project with a link."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(
            app,
            [
                "add",
                "project",
                "--name",
                "Open Source Project",
                "--description",
                "Contributions to open source",
                "--link",
                "https://github.com/user/project",
            ],
        )

        assert result.exit_code == 0
        assert "Created project" in result.stdout

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        project = storage.load_project("Open Source Project")
        assert project is not None
        assert project.name == "Open Source Project"
        assert project.link == "https://github.com/user/project"


def test_add_job_command(temp_dir):
    """Test adding a job without URL (manual entry)."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["add", "job", "--name", "Software Engineer Position"])

        assert result.exit_code == 0
        assert "Created job application" in result.stdout
        assert "Application ID:" in result.stdout

        # Check that directory was created (application ID includes date, so we check pattern)
        applications_dir = temp_dir / "applications"
        assert applications_dir.exists()
        # Should have one directory matching the pattern
        app_dirs = [d for d in applications_dir.iterdir() if d.is_dir()]
        assert len(app_dirs) == 1

        # Verify job file was created
        job_file = app_dirs[0] / "job-description.md"
        assert job_file.exists()

        # Verify content
        from cveasy.storage import MarkdownStorage

        storage = MarkdownStorage(temp_dir)
        application_id = app_dirs[0].name
        job = storage.load_job(application_id)
        assert job is not None
        assert job.name == "Software Engineer Position"


def test_add_job_command_with_url(temp_dir):
    """Test adding a job with URL (scraping)."""
    runner = CliRunner()

    application_id = "software-engineer-position-20240101"
    filepath = temp_dir / "applications" / application_id / "job-description.md"

    mock_service = MagicMock()
    mock_service.create_application.return_value = (application_id, filepath)

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        with patch("cveasy.commands.add.ApplicationService", return_value=mock_service):
            result = runner.invoke(
                app,
                [
                    "add",
                    "job",
                    "--name",
                    "Software Engineer Position",
                    "--url",
                    "https://example.com/job",
                ],
            )

            assert result.exit_code == 0
            assert "Scraping job description" in result.stdout
            assert "Created job application" in result.stdout

            # Verify service was called
            mock_service.create_application.assert_called_once_with(
                "Software Engineer Position", "https://example.com/job"
            )


def test_add_job_command_with_url_scraping_fails(temp_dir):
    """Test adding a job with URL when scraping fails."""
    runner = CliRunner()

    from cveasy.exceptions import DataImportError

    application_id = "software-engineer-position-20240101"

    # Mock the scraper to raise ImportError, but service should handle it gracefully
    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        with patch("cveasy.services.application_service.JobScraper") as mock_scraper_class:
            mock_scraper = mock_scraper_class.return_value
            mock_scraper.scrape.side_effect = DataImportError("Failed to scrape")

            result = runner.invoke(
                app,
                [
                    "add",
                    "job",
                    "--name",
                    "Software Engineer Position",
                    "--url",
                    "https://example.com/job",
                ],
            )

            assert result.exit_code == 0
            assert "Created job application" in result.stdout

            # Verify job was still created with empty content
            applications_dir = temp_dir / "applications"
            app_dirs = [d for d in applications_dir.iterdir() if d.is_dir()]
            assert len(app_dirs) == 1

            from cveasy.storage import MarkdownStorage

            storage = MarkdownStorage(temp_dir)
            application_id = app_dirs[0].name
            job = storage.load_job(application_id)
            assert job is not None
            assert job.name == "Software Engineer Position"
            assert job.content == ""
