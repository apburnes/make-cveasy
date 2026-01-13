"""Tests for Word export."""

from pathlib import Path
import tempfile
from cveasy.export.word import export_to_word


def test_export_to_word():
    """Test Word export."""
    resume_text = "# John Doe\n\n## Experience\n\nSoftware Engineer"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "resume.docx"

        result_path = export_to_word(resume_text, output_path)

        assert result_path.exists()
        assert result_path.suffix == ".docx"
