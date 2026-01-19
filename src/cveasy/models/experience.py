"""Experience model."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from cveasy.models.utils import generate_slug


class Experience(BaseModel):
    """Experience model with frontmatter metadata."""

    title: str = Field(..., description="Job title")
    slug: str = Field(default="", description="URL-safe slug for the experience")
    organization: str = Field(..., description="Organization/company name")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD) or 'Present'")
    location: Optional[str] = Field(None, description="Location")
    related_skills: List[str] = Field(default_factory=list, description="Related skill IDs")
    related_stories: List[str] = Field(default_factory=list, description="Related story IDs")
    content: str = Field(default="", description="Summary of the experience in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

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
        if self.related_skills:
            data["related_skills"] = self.related_skills
        if self.related_stories:
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
            created = datetime.fromisoformat(data["created"]) if isinstance(data["created"], str) else data["created"]
        if "updated" in data:
            updated = datetime.fromisoformat(data["updated"]) if isinstance(data["updated"], str) else data["updated"]

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
