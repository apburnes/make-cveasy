"""Tests for PDF export."""

from pathlib import Path
import tempfile
from cveasy.export.pdf import export_to_pdf


def test_export_to_pdf():
    """Test PDF export."""
    resume_text = "# John Doe\n\n## Experience\n\nSoftware Engineer"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "resume.pdf"

        result_path = export_to_pdf(resume_text, output_path)

        assert result_path.exists()
        assert result_path.suffix == ".pdf"
