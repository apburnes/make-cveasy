"""Link model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Link(BaseModel):
    """Link model with frontmatter metadata."""

    name: str = Field(..., description="Link name (e.g., LinkedIn, GitHub)")
    description: str = Field(..., description="Description of the link")
    url: str = Field(..., description="URL")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "name": self.name,
            "description": self.description,
            "url": self.url,
        }

        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Link":
        """Create Link from frontmatter dictionary."""
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
            url=data.get("url", ""),
            created=created,
            updated=updated,
        )
