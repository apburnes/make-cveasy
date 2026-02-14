"""Skill model."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, model_validator

from cveasy.models.utils import generate_slug


class Skill(BaseModel):
    """Skill model with frontmatter metadata."""

    name: str = Field(..., description="Name of the skill")
    slug: str = Field(default="", description="URL-safe slug for the skill")
    category: Optional[str] = Field(None, description="Category of the skill")
    years: Optional[int] = Field(None, description="Years of experience")
    proficiency: Optional[str] = Field(None, description="Proficiency level")
    related_experiences: List[str] = Field(
        default_factory=list, description="Related experience slugs"
    )
    content: str = Field(default="", description="Verbose summary in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    @model_validator(mode="after")
    def generate_slug_if_missing(self) -> "Skill":
        """Generate slug from name if not already set."""
        if not self.slug:
            self.slug = generate_slug(self.name)
        return self

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "name": self.name,
            "slug": self.slug,
        }

        if self.category:
            data["category"] = self.category
        if self.years is not None:
            data["years"] = self.years
        if self.proficiency:
            data["proficiency"] = self.proficiency
        data["related_experiences"] = self.related_experiences
        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Skill":
        """Create Skill from frontmatter dictionary."""
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
            category=data.get("category"),
            years=data.get("years"),
            proficiency=data.get("proficiency"),
            related_experiences=data.get("related_experiences", data.get("related_experience", [])),
            content=content,
            created=created,
            updated=updated,
        )
