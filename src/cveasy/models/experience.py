"""Experience model."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class Experience(BaseModel):
    """Experience model with frontmatter metadata."""

    title: str = Field(..., description="Job title")
    organization: str = Field(..., description="Organization/company name")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD) or 'Present'")
    location: Optional[str] = Field(None, description="Location")
    related_skills: List[str] = Field(default_factory=list, description="Related skill IDs")
    related_stories: List[str] = Field(default_factory=list, description="Related story IDs")
    content: str = Field(default="", description="Summary of the experience in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "title": self.title,
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

        return cls(
            title=data.get("title", ""),
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
