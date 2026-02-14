"""Experience model."""

import re
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from cveasy.models.utils import generate_slug


class Experience(BaseModel):
    """Experience model with frontmatter metadata."""

    title: str = Field(..., description="Job title")
    slug: str = Field(default="", description="URL-safe slug for the experience")
    organization: str = Field(..., description="Organization/company name")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM) or 'Present'")
    location: Optional[str] = Field(None, description="Location")
    related_skills: List[str] = Field(default_factory=list, description="Related skill IDs")
    related_stories: List[str] = Field(default_factory=list, description="Related story IDs")
    content: str = Field(default="", description="Summary of the experience in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    @field_validator("start_date", mode="before")
    @classmethod
    def validate_start_date(cls, v: Optional[str]) -> Optional[str]:
        """Normalize start_date to YYYY-MM format."""
        if v is None or v == "":
            return v
        v = str(v).strip()
        # YYYY-MM-DD -> YYYY-MM
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v[:7]
        # YYYY-MM passes through
        if re.match(r"^\d{4}-\d{2}$", v):
            return v
        # YYYY passes through
        if re.match(r"^\d{4}$", v):
            return v
        return v

    @field_validator("end_date", mode="before")
    @classmethod
    def validate_end_date(cls, v: Optional[str]) -> Optional[str]:
        """Normalize end_date to YYYY-MM format, and 'present' to 'Present'."""
        if v is None or v == "":
            return v
        v = str(v).strip()
        # Normalize "present" (any case) to "Present"
        if v.lower() == "present":
            return "Present"
        # YYYY-MM-DD -> YYYY-MM
        if re.match(r"^\d{4}-\d{2}-\d{2}$", v):
            return v[:7]
        # YYYY-MM passes through
        if re.match(r"^\d{4}-\d{2}$", v):
            return v
        # YYYY passes through
        if re.match(r"^\d{4}$", v):
            return v
        return v

    @model_validator(mode="after")
    def generate_slug_if_missing(self) -> "Experience":
        """Generate slug from title if not already set."""
        if not self.slug:
            self.slug = generate_slug(self.title)
        return self

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "title": self.title,
            "slug": self.slug,
            "organization": self.organization,
        }

        if self.start_date:
            data["start_date"] = self.start_date
        if self.end_date:
            data["end_date"] = self.end_date
        if self.location:
            data["location"] = self.location
        data["related_skills"] = self.related_skills
        data["related_stories"] = self.related_stories
        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Experience":
        """Create Experience from frontmatter dictionary."""
        # Parse dates if present
        created = None
        updated = None
        if "created" in data:
            created = (
                datetime.fromisoformat(data["created"])
                if isinstance(data["created"], str)
                else data["created"]
            )
        if "updated" in data:
            updated = (
                datetime.fromisoformat(data["updated"])
                if isinstance(data["updated"], str)
                else data["updated"]
            )

        # Generate slug if not present (for backward compatibility)
        slug = data.get("slug")
        if not slug and data.get("title"):
            slug = generate_slug(data.get("title", ""))

        return cls(
            title=data.get("title", ""),
            slug=slug or "",
            organization=data.get("organization", ""),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            location=data.get("location"),
            related_skills=data.get("related_skills", []),
            related_stories=data.get("related_stories", []),
            content=content,
            created=created,
            updated=updated,
        )
