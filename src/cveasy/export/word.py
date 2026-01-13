"""Word document export functionality."""

from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
import re


def markdown_to_docx_paragraphs(doc: Document, text: str):
    """Convert markdown text to docx paragraphs."""
    lines = text.split('\n')

    for line in lines:
        line = line.strip()

        if not line:
            continue

        # Headers
        if line.startswith('# '):
            p = doc.add_heading(line[2:], level=1)
            continue
        elif line.startswith('## '):
            p = doc.add_heading(line[3:], level=2)
            continue
        elif line.startswith('### '):
            p = doc.add_heading(line[4:], level=3)
            continue

        # Lists
        if line.startswith('- ') or line.startswith('* '):
            list_text = line[2:].strip()
            # Remove markdown formatting
            list_text = re.sub(r'\*\*(.+?)\*\*', r'\1', list_text)
            list_text = re.sub(r'\*(.+?)\*', r'\1', list_text)
            p = doc.add_paragraph(list_text, style='List Bullet')
            continue

        # Regular paragraph
        p = doc.add_paragraph()

        # Process inline formatting
        parts = re.split(r'(\*\*.*?\*\*|\*.*?\*|\[.*?\]\(.*?\))', line)

        for part in parts:
            if not part:
                continue

            # Bold
            if part.startswith('**') and part.endswith('**'):
                run = p.add_run(part[2:-2])
                run.bold = True
            # Italic
            elif part.startswith('*') and part.endswith('*') and not part.startswith('**'):
                run = p.add_run(part[1:-1])
                run.italic = True
            # Links (just use text)
            elif part.startswith('[') and '](' in part:
                link_text = re.match(r'\[(.+?)\]', part).group(1)
                run = p.add_run(link_text)
            else:
                run = p.add_run(part)

        # Set font size
        for run in p.runs:
            run.font.size = Pt(11)


def export_to_word(resume_text: str, output_path: Path) -> Path:
    """
    Export resume to Word document.

    Args:
        resume_text: Resume content in markdown
        output_path: Output file path

    Returns:
        Path to created Word document
    """
    doc = Document()

    # Set margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1)
        section.right_margin = Inches(1)

    # Convert markdown to docx
    markdown_to_docx_paragraphs(doc, resume_text)

    # Save document
    doc.save(str(output_path))

    return output_path
