"""Shared style configuration for resume exports."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ResumeStyle:
    """Standardized style configuration for resume exports."""

    # Font sizes (in points)
    font_size_header: int = 20
    font_size_subheader: int = 16
    font_size_body: int = 11
    font_size_small: int = 10

    # Heading-specific font sizes (in points) - descending
    font_size_h1: int = 20  # Heading 1 (name)
    font_size_h2: int = 16  # Heading 2 (section titles)
    font_size_h3: int = 14  # Heading 3 (subsection titles)

    # Heading font weights - descending
    font_weight_h1: int = 700  # Bold
    font_weight_h2: int = 600  # Semi-bold
    font_weight_h3: int = 500  # Medium

    # Margins (in inches)
    margin_top: float = 1.0
    margin_bottom: float = 0.75
    margin_left: float = 1.0
    margin_right: float = 1.0

    # Spacing (in inches)
    spacing_section_major: float = 0.25  # Between major sections
    spacing_section_minor: float = 0.15  # Between subsections
    spacing_paragraph: float = 0.12  # Between paragraphs
    spacing_list_item: float = 0.05  # Between list items
    spacing_heading_after: float = 0.03  # After headings (much smaller)
    spacing_heading_before: float = 0.05  # Before headings (much smaller)

    # Line heights (multiplier)
    line_height_header: float = 1.2
    line_height_body: float = 1.3

    # Font families (optional, can be None for defaults)
    font_family: Optional[str] = None
    font_family_header: Optional[str] = None

    # List formatting
    list_bullet: str = "•"
    list_indent: float = 0.25  # Indentation for list items (in inches)

    # Link formatting
    link_preserve_url: bool = True  # Whether to preserve URLs in links


# Default style instance
DEFAULT_STYLE = ResumeStyle()

# Export commonly used values for convenience
FONT_SIZE_HEADER = DEFAULT_STYLE.font_size_header
FONT_SIZE_SUBHEADER = DEFAULT_STYLE.font_size_subheader
FONT_SIZE_BODY = DEFAULT_STYLE.font_size_body
FONT_SIZE_SMALL = DEFAULT_STYLE.font_size_small

# Heading-specific font sizes
FONT_SIZE_H1 = DEFAULT_STYLE.font_size_h1
FONT_SIZE_H2 = DEFAULT_STYLE.font_size_h2
FONT_SIZE_H3 = DEFAULT_STYLE.font_size_h3

# Heading font weights
FONT_WEIGHT_H1 = DEFAULT_STYLE.font_weight_h1
FONT_WEIGHT_H2 = DEFAULT_STYLE.font_weight_h2
FONT_WEIGHT_H3 = DEFAULT_STYLE.font_weight_h3

MARGIN_TOP = DEFAULT_STYLE.margin_top
MARGIN_BOTTOM = DEFAULT_STYLE.margin_bottom
MARGIN_LEFT = DEFAULT_STYLE.margin_left
MARGIN_RIGHT = DEFAULT_STYLE.margin_right

SPACING_SECTION_MAJOR = DEFAULT_STYLE.spacing_section_major
SPACING_SECTION_MINOR = DEFAULT_STYLE.spacing_section_minor
SPACING_PARAGRAPH = DEFAULT_STYLE.spacing_paragraph
SPACING_LIST_ITEM = DEFAULT_STYLE.spacing_list_item
SPACING_HEADING_AFTER = DEFAULT_STYLE.spacing_heading_after
SPACING_HEADING_BEFORE = DEFAULT_STYLE.spacing_heading_before

LINE_HEIGHT_HEADER = DEFAULT_STYLE.line_height_header
LINE_HEIGHT_BODY = DEFAULT_STYLE.line_height_body

LIST_BULLET = DEFAULT_STYLE.list_bullet
LIST_INDENT = DEFAULT_STYLE.list_indent
