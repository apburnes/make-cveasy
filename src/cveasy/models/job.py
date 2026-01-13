"""Job model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Job(BaseModel):
    """Job application model with frontmatter metadata."""

    name: str = Field(..., description="Job application name")
    title: Optional[str] = Field(None, description="Job title")
    location: Optional[str] = Field(None, description="Location")
    requirements: Optional[str] = Field(None, description="Requirements")
    pay: Optional[str] = Field(None, description="Pay/salary range")
    content: str = Field(default="", description="Full job description text")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "name": self.name,
        }

        if self.title:
            data["title"] = self.title
        if self.location:
            data["location"] = self.location
        if self.requirements:
            data["requirements"] = self.requirements
        if self.pay:
            data["pay"] = self.pay
        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Job":
        """Create Job from frontmatter dictionary."""
        # Parse dates if present
        created = None
        updated = None
        if "created" in data:
            created = datetime.fromisoformat(data["created"]) if isinstance(data["created"], str) else data["created"]
        if "updated" in data:
            updated = datetime.fromisoformat(data["updated"]) if isinstance(data["updated"], str) else data["updated"]

        return cls(
            name=data.get("name", ""),
            title=data.get("title"),
            location=data.get("location"),
            requirements=data.get("requirements"),
            pay=data.get("pay"),
            content=content,
            created=created,
            updated=updated,
        )
