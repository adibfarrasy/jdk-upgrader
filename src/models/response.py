from typing import List
from pydantic import BaseModel, Field


class Location(BaseModel):
    """Represents a location in a file for precise change targeting."""

    file_path: str = Field(description="Relative path to the file")
    start_line: int = Field(description="Starting line number (1-indexed)")
    end_line: int = Field(
        description="Ending line number (1-indexed, inclusive)")

    def __str__(self) -> str:
        if self.start_line == self.end_line:
            return f"{self.file_path}:{self.start_line}"
        return f"{self.file_path}:{self.start_line}-{self.end_line}"


class Change(BaseModel):
    """Represents a single code change with context."""

    reason: str = Field(description="Why this change is needed")
    location: Location = Field(description="Where to make the change")
    before: str = Field(description="Original code to replace")
    after: str = Field(description="New code to replace with")

    def __str__(self) -> str:

        def format_lines(text: str, prefix: str, color: str) -> str:
            if not text.strip():
                return ""
            lines = text.strip().split('\n')
            return '\n'.join(f"[{color}]{prefix} {line}[/{color}]" for line in lines)

        before_diff = format_lines(self.before, "-", "red")
        after_diff = format_lines(self.after, "+", "green")

        diff_content = '\n'.join(
            [d for d in [before_diff, after_diff] if d.strip()])

        return f"[{self.location}] {self.reason}\n\n{diff_content}"


class StructuredResponse(BaseModel):
    """Unified response format for all analyzers."""

    summary: str = Field(description="High-level summary of response")
    changes: List[Change] = Field(
        description="List of specific changes to make")

    def __str__(self) -> str:
        result = f"Summary: {self.summary}\n"
        if self.changes:
            result += "\nChanges:\n" + \
                "\n\n".join(str(change) for change in self.changes)
        else:
            result += "\nNo changes needed."
        return result
