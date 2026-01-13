"""Project model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Project(BaseModel):
    """Project model with frontmatter metadata."""

    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    link: Optional[str] = Field(None, description="Project URL/link")
    content: str = Field(default="", description="Summary of the project in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "name": self.name,
            "description": self.description,
        }

        if self.link:
            data["link"] = self.link
        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Project":
        """Create Project from frontmatter dictionary."""
        # Parse dates if present
        created = None
        updated = None
        if "created" in data:
            created = datetime.fromisoformat(data["created"]) if isinstance(data["created"], str) else data["created"]
        if "updated" in data:
            updated = datetime.fromisoformat(data["updated"]) if isinstance(data["updated"], str) else data["updated"]

        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            link=data.get("link"),
            content=content,
            created=created,
            updated=updated,
        )
