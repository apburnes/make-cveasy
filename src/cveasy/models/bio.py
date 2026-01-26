"""Bio model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, model_validator

from cveasy.models.utils import generate_slug


class Bio(BaseModel):
    """Bio model with frontmatter metadata."""

    name: str = Field(..., description="User's name")
    slug: str = Field(default="", description="URL-safe slug for the bio")
    location: str = Field(default="", description="User's location")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def generate_slug_if_missing(self) -> "Bio":
        """Generate slug from name if not already set."""
        if not self.slug:
            self.slug = generate_slug(self.name)
        return self

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "name": self.name,
            "slug": self.slug,
            "location": self.location,
        }

        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Bio":
        """Create Bio from frontmatter dictionary."""
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
        if not slug and data.get("name"):
            slug = generate_slug(data.get("name", ""))

        return cls(
            name=data.get("name", ""),
            slug=slug or "",
            location=data.get("location", ""),
            created=created,
            updated=updated,
        )
