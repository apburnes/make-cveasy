"""Story model."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from cveasy.models.utils import generate_slug


class Story(BaseModel):
    """Story model with frontmatter metadata."""

    title: str = Field(..., description="Story title")
    slug: str = Field(default="", description="URL-safe slug for the story")
    context: Optional[str] = Field(None, description="Context of the story")
    outcome: Optional[str] = Field(None, description="Outcome of the story")
    related_experiences: List[str] = Field(
        default_factory=list, description="Related experience slugs"
    )
    content: str = Field(default="", description="Detailed description in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def generate_slug_if_missing(self) -> "Story":
        """Generate slug from title if not already set."""
        if not self.slug:
            self.slug = generate_slug(self.title)
        return self

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "title": self.title,
            "slug": self.slug,
        }

        if self.context:
            data["context"] = self.context
        if self.outcome:
            data["outcome"] = self.outcome
        data["related_experiences"] = self.related_experiences
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
            context=data.get("context"),
            outcome=data.get("outcome"),
            related_experiences=data.get("related_experiences", []),
            content=content,
            created=created,
            updated=updated,
        )
