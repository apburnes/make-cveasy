"""PDF export functionality."""

from pathlib import Path
from typing import TYPE_CHECKING
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_LEFT
import re

from cveasy.export.styles import DEFAULT_STYLE

if TYPE_CHECKING:
    from cveasy.export.styles import ResumeStyle


def markdown_to_paragraphs(
    text: str,
    styles,
    resume_style: "ResumeStyle" = DEFAULT_STYLE,  # noqa: F821
):
    """Convert markdown text to ReportLab paragraphs."""
    elements = []
    lines = text.split("\n")

    current_paragraph = []
    in_list = False
    previous_was_header = False

    for line in lines:
        line = line.strip()

        # Skip markdown dividers
        if line == "---" or line.startswith("---"):
            continue

        if not line:
            if current_paragraph:
                elements.append(Paragraph(" ".join(current_paragraph), styles["Normal"]))
                elements.append(Spacer(1, resume_style.spacing_paragraph * inch))
                current_paragraph = []
            in_list = False
            previous_was_header = False
            continue

        # Headers
        if line.startswith("# "):
            if current_paragraph:
                elements.append(Paragraph(" ".join(current_paragraph), styles["Normal"]))
                elements.append(Spacer(1, resume_style.spacing_paragraph * inch))
                current_paragraph = []
            # Add spacing before header if not first element
            if elements and not previous_was_header:
                elements.append(Spacer(1, resume_style.spacing_heading_before * inch))
            elements.append(Paragraph(line[2:], styles["Heading1"]))
            elements.append(Spacer(1, resume_style.spacing_heading_after * inch))
            previous_was_header = True
            in_list = False
            continue
        elif line.startswith("## "):
            if current_paragraph:
                elements.append(Paragraph(" ".join(current_paragraph), styles["Normal"]))
                elements.append(Spacer(1, resume_style.spacing_paragraph * inch))
                current_paragraph = []
            # Add spacing before header if not first element
            if elements and not previous_was_header:
                elements.append(Spacer(1, resume_style.spacing_heading_before * inch))
            elements.append(Paragraph(line[3:], styles["Heading2"]))
            elements.append(Spacer(1, resume_style.spacing_heading_after * inch))
            previous_was_header = True
            in_list = False
            continue
        elif line.startswith("### "):
            if current_paragraph:
                elements.append(Paragraph(" ".join(current_paragraph), styles["Normal"]))
                elements.append(Spacer(1, resume_style.spacing_paragraph * inch))
                current_paragraph = []
            # Add spacing before subheader
            if elements and not previous_was_header:
                elements.append(Spacer(1, resume_style.spacing_heading_before * inch))
            elements.append(Paragraph(line[4:], styles["Heading3"]))
            elements.append(Spacer(1, resume_style.spacing_heading_after * inch))
            previous_was_header = True
            in_list = False
            continue

        previous_was_header = False

        # Lists
        if line.startswith("- ") or line.startswith("* "):
            if current_paragraph:
                elements.append(Paragraph(" ".join(current_paragraph), styles["Normal"]))
                elements.append(Spacer(1, resume_style.spacing_paragraph * inch))
                current_paragraph = []
            list_text = line[2:].strip()
            # Remove markdown formatting but preserve bold/italic
            list_text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", list_text)
            list_text = re.sub(r"\*(.+?)\*", r"<i>\1</i>", list_text)
            # Handle links - preserve URL if configured
            if resume_style.link_preserve_url:
                list_text = re.sub(
                    r"\[(.+?)\]\((.+?)\)", r'\1 (<link href="\2" color="blue">\2</link>)', list_text
                )
            else:
                list_text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", list_text)
            elements.append(Paragraph(f"{resume_style.list_bullet} {list_text}", styles["Normal"]))
            in_list = True
            continue

        # Regular text
        # Remove markdown formatting but preserve bold/italic
        line = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", line)
        line = re.sub(r"\*(.+?)\*", r"<i>\1</i>", line)
        # Handle links - preserve URL if configured
        if resume_style.link_preserve_url:
            line = re.sub(
                r"\[(.+?)\]\((.+?)\)", r'\1 (<link href="\2" color="blue">\2</link>)', line
            )
        else:
            line = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", line)

        if in_list:
            elements.append(Spacer(1, resume_style.spacing_list_item * inch))
            in_list = False

        current_paragraph.append(line)

    if current_paragraph:
        elements.append(Paragraph(" ".join(current_paragraph), styles["Normal"]))

    return elements


def export_to_pdf(
    resume_text: str,
    output_path: Path,
    resume_style: "ResumeStyle" = DEFAULT_STYLE,  # noqa: F821
) -> Path:
    """
    Export resume to PDF.

    Args:
        resume_text: Resume content in markdown
        output_path: Output file path
        resume_style: Style configuration to use (defaults to DEFAULT_STYLE)

    Returns:
        Path to created PDF file
    """
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=resume_style.margin_right * 72,  # Convert inches to points
        leftMargin=resume_style.margin_left * 72,
        topMargin=resume_style.margin_top * 72,
        bottomMargin=resume_style.margin_bottom * 72,
    )

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    # Modify the existing Normal style instead of trying to replace it
    # (StyleSheet1 doesn't support item assignment)
    styles["Normal"].fontSize = resume_style.font_size_body
    styles["Normal"].leading = resume_style.font_size_body * resume_style.line_height_body
    styles["Normal"].spaceAfter = resume_style.spacing_paragraph * 72  # Convert to points
    styles["Normal"].alignment = TA_LEFT

    # Update header styles with descending font sizes and weights
    styles["Heading1"].fontSize = resume_style.font_size_h1
    styles["Heading1"].leading = resume_style.font_size_h1 * resume_style.line_height_header
    styles["Heading1"].spaceAfter = resume_style.spacing_heading_after * 72
    styles["Heading1"].fontName = "Helvetica-Bold"  # Bold weight (700)

    styles["Heading2"].fontSize = resume_style.font_size_h2
    styles["Heading2"].leading = resume_style.font_size_h2 * resume_style.line_height_header
    styles["Heading2"].spaceAfter = resume_style.spacing_heading_after * 72
    # Semi-bold (600) - use Helvetica-Bold as closest approximation
    styles["Heading2"].fontName = "Helvetica-Bold"

    styles["Heading3"].fontSize = resume_style.font_size_h3
    styles["Heading3"].leading = resume_style.font_size_h3 * resume_style.line_height_header
    styles["Heading3"].spaceAfter = resume_style.spacing_heading_after * 72
    # Medium (500) - use regular Helvetica
    styles["Heading3"].fontName = "Helvetica"

    # Apply font families if specified
    if resume_style.font_family:
        styles["Normal"].fontName = resume_style.font_family
    if resume_style.font_family_header:
        styles["Heading1"].fontName = resume_style.font_family_header
        styles["Heading2"].fontName = resume_style.font_family_header
        styles["Heading3"].fontName = resume_style.font_family_header

    # Convert markdown to paragraphs
    paragraphs = markdown_to_paragraphs(resume_text, styles, resume_style)
    elements.extend(paragraphs)

    # Build PDF
    doc.build(elements)

    return output_path
