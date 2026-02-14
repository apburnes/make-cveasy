"""Education model."""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

from cveasy.models.utils import generate_slug


class Education(BaseModel):
    """Education model with frontmatter metadata."""

    name: str = Field(..., description="Education name/title")
    slug: str = Field(default="", description="URL-safe slug for the education")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM) or 'Present'")
    degree: Optional[str] = Field(None, description="Degree type (e.g., Bachelor of Science)")
    certificate: Optional[str] = Field(None, description="Certificate name")
    organization: Optional[str] = Field(None, description="School/institution name")
    content: str = Field(default="", description="Additional description in markdown")
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
    def generate_slug_if_missing(self) -> "Education":
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

        if self.start_date:
            data["start_date"] = self.start_date
        if self.end_date:
            data["end_date"] = self.end_date
        if self.degree:
            data["degree"] = self.degree
        if self.certificate:
            data["certificate"] = self.certificate
        if self.organization:
            data["organization"] = self.organization
        if self.created:
            data["created"] = self.created.isoformat()
        if self.updated:
            data["updated"] = self.updated.isoformat()

        return data

    @classmethod
    def from_frontmatter_dict(cls, data: dict, content: str = "") -> "Education":
        """Create Education from frontmatter dictionary."""
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
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            degree=data.get("degree"),
            certificate=data.get("certificate"),
            organization=data.get("organization"),
            content=content,
            created=created,
            updated=updated,
        )
