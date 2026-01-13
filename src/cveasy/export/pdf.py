"""PDF export functionality."""

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import re


def markdown_to_paragraphs(text: str, styles):
    """Convert markdown text to ReportLab paragraphs."""
    elements = []
    lines = text.split('\n')

    current_paragraph = []
    in_list = False

    for line in lines:
        line = line.strip()

        if not line:
            if current_paragraph:
                elements.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                elements.append(Spacer(1, 0.1 * inch))
                current_paragraph = []
            in_list = False
            continue

        # Headers
        if line.startswith('# '):
            if current_paragraph:
                elements.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                current_paragraph = []
            elements.append(Paragraph(line[2:], styles['Heading1']))
            elements.append(Spacer(1, 0.2 * inch))
            continue
        elif line.startswith('## '):
            if current_paragraph:
                elements.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                current_paragraph = []
            elements.append(Paragraph(line[3:], styles['Heading2']))
            elements.append(Spacer(1, 0.15 * inch))
            continue
        elif line.startswith('### '):
            if current_paragraph:
                elements.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                current_paragraph = []
            elements.append(Paragraph(line[4:], styles['Heading3']))
            elements.append(Spacer(1, 0.1 * inch))
            continue

        # Lists
        if line.startswith('- ') or line.startswith('* '):
            if current_paragraph:
                elements.append(Paragraph(' '.join(current_paragraph), styles['Normal']))
                current_paragraph = []
            list_text = line[2:].strip()
            # Remove markdown formatting
            list_text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', list_text)
            elements.append(Paragraph(f"• {list_text}", styles['Normal']))
            in_list = True
            continue

        # Regular text
        # Remove markdown formatting
        line = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', line)
        line = re.sub(r'\*(.+?)\*', r'<i>\1</i>', line)
        line = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', line)  # Remove links, keep text

        if in_list:
            elements.append(Spacer(1, 0.05 * inch))
            in_list = False

        current_paragraph.append(line)

    if current_paragraph:
        elements.append(Paragraph(' '.join(current_paragraph), styles['Normal']))

    return elements


def export_to_pdf(resume_text: str, output_path: Path) -> Path:
    """
    Export resume to PDF.

    Args:
        resume_text: Resume content in markdown
        output_path: Output file path

    Returns:
        Path to created PDF file
    """
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    # Modify the existing Normal style instead of trying to replace it
    # (StyleSheet1 doesn't support item assignment)
    styles['Normal'].fontSize = 11
    styles['Normal'].leading = 14
    styles['Normal'].spaceAfter = 6

    # Convert markdown to paragraphs
    paragraphs = markdown_to_paragraphs(resume_text, styles)
    elements.extend(paragraphs)

    # Build PDF
    doc.build(elements)

    return output_path
