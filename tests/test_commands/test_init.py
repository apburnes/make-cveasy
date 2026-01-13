"""Tests for init command."""

from typer.testing import CliRunner
from cveasy.cli import app
from pathlib import Path
import tempfile
import shutil


def test_init_command():
    """Test init command creates project structure."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir) / "test-resume"

        # Use --project option to specify the full project path
        # Note: when --project is specified, -n is ignored, so we pass the full path
        result = runner.invoke(
            app, ["init", "--project", str(project_path)]
        )

        # Check command succeeded
        assert result.exit_code == 0

        # Verify project directory was created
        assert project_path.exists()
        assert project_path.is_dir()

        # Verify subdirectories were created
        expected_subdirs = [
            "skills",
            "experiences",
            "stories",
            "links",
            "projects",
            "applications",
            "resume",
            "education",
        ]
        for subdir in expected_subdirs:
            assert (project_path / subdir).exists()
            assert (project_path / subdir).is_dir()

        # Verify files were created
        assert (project_path / "README.md").exists()
        assert (project_path / ".env.example").exists()
        assert (project_path / ".gitignore").exists()
        assert (project_path / "bio.md").exists()

        # Verify git was initialized
        assert (project_path / ".git").exists()

        # Clean up the test-resume directory
        if project_path.exists():
            shutil.rmtree(project_path)
