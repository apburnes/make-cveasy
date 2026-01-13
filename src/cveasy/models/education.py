"""Education model."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Education(BaseModel):
    """Education model with frontmatter metadata."""

    name: str = Field(..., description="Education name/title")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD) or 'Present'")
    degree: Optional[str] = Field(None, description="Degree type (e.g., Bachelor of Science)")
    certificate: Optional[str] = Field(None, description="Certificate name")
    organization: Optional[str] = Field(None, description="School/institution name")
    content: str = Field(default="", description="Additional description in markdown")
    created: Optional[datetime] = Field(default_factory=datetime.now)
    updated: Optional[datetime] = Field(default_factory=datetime.now)

    def to_frontmatter_dict(self) -> dict:
        """Convert to dictionary for frontmatter."""
        data = {
            "name": self.name,
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
            created = datetime.fromisoformat(data["created"]) if isinstance(data["created"], str) else data["created"]
        if "updated" in data:
            updated = datetime.fromisoformat(data["updated"]) if isinstance(data["updated"], str) else data["updated"]

        return cls(
            name=data.get("name", ""),
            start_date=data.get("start_date"),
            end_date=data.get("end_date"),
            degree=data.get("degree"),
            certificate=data.get("certificate"),
            organization=data.get("organization"),
            content=content,
            created=created,
            updated=updated,
        )
