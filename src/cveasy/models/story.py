"""Story model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Story(BaseModel):
    """Story model with frontmatter metadata."""

    title: str = Field(..., description="Story title")
    context: Optional[str] = Field(None, description="Context of the story")
    outcome: Optional[str] = Field(None, description="Outcome of the story")
    content: str = Field(default="", description="Detailed description in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "title": self.title,
        }

        if self.context:
            data["context"] = self.context
        if self.outcome:
            data["outcome"] = self.outcome
        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Story":
        """Create Story from frontmatter dictionary."""
        # Parse dates if present
        created = None
        updated = None
        if "created" in data:
            created = datetime.fromisoformat(data["created"]) if isinstance(data["created"], str) else data["created"]
        if "updated" in data:
            updated = datetime.fromisoformat(data["updated"]) if isinstance(data["updated"], str) else data["updated"]

        return cls(
            title=data.get("title", ""),
            context=data.get("context"),
            outcome=data.get("outcome"),
            content=content,
            created=created,
            updated=updated,
        )
