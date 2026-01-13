"""Tests for add command."""

import pytest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner

from cveasy.cli import app


def test_add_education_command(temp_dir):
    """Test adding an education entry."""
    runner = CliRunner()

    with patch("cveasy.commands.add.get_project_path", return_value=temp_dir):
        result = runner.invoke(app, ["add", "education", "--name", "Bachelor of Science in Computer Science"])

        assert result.exit_code == 0
        assert "Created education" in result.stdout

        # Check that file was created
        education_file = temp_dir / "education" / "bachelor-of-science-in-computer-science.md"
        assert education_file.exists()


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

        # Check that file was created
        education_file = temp_dir / "education" / "master-of-science.md"
        assert education_file.exists()

        # Verify content
        from cveasy.storage import MarkdownStorage
        storage = MarkdownStorage(temp_dir)
        education = storage.load_education("Master of Science")
        assert education is not None
        assert education.name == "Master of Science"
        assert education.start_date == "2020-09-01"
        assert education.end_date == "2022-05-15"
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
