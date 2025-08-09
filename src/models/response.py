from typing import List
from pydantic import BaseModel, Field


class Location(BaseModel):
    """Represents a location in a file for precise change targeting."""

    file_path: str = Field(description="Relative path to the file")
    start_line: int = Field(description="Starting line number (1-indexed)")
    end_line: int = Field(
        description="Ending line number (1-indexed, inclusive)")


class Change(BaseModel):
    """Represents a single code change with context."""

    reason: str = Field(description="Why this change is needed")
    location: Location = Field(description="Where to make the change")
    before: str = Field(description="Original code to replace")
    after: str = Field(description="New code to replace with")


class StructuredResponse(BaseModel):
    """Unified response format for all analyzers."""

    summary: str = Field(description="High-level summary of response")
    changes: List[Change] = Field(
        description="List of specific changes to make")
