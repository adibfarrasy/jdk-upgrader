import re
from typing import List, Tuple
from dataclasses import dataclass
from rich.console import Console


@dataclass
class CodeBlock:
    """Represents an extracted code block."""

    content: str
    start_line: int
    end_line: int
    file_path: str
    matched_keywords: List[str]

    @property
    def line_count(self) -> int:
        return self.end_line - self.start_line + 1


class CodeBlockExtractor:
    """
    Extracts upgradable code blocks from source files.

    This class optimizes LLM usage by extracting only relevant code blocks
    instead of passing entire files.

    It trades broader context for cost efficiency by identifying keywords and
    extracting their smallest enclosing blocks.

    Cost optimization strategy:
    - Regex pre-filtering to avoid LLM calls on irrelevant files
    - Block-level extraction instead of file-level analysis
    - Merging overlapping regions to prevent duplicate processing
    - Size warnings to catch unexpectedly large blocks
    """

    def __init__(self, max_block_lines: int = 20, console=None):
        """
        Initialize the code block extractor.

        Args:
            max_block_lines: Warning threshold for large blocks
        """
        self.max_block_lines = max_block_lines
        self.console = console or Console()

    def extract_blocks(
        self, file_path: str, content: str, keywords: List[str]
    ) -> List[CodeBlock]:
        """
        Extract all relevant code blocks from file content.

        Args:
            file_path: Path to the source file
            content: File content as string
            keywords: List of regex patterns to search for

        Returns:
            List of extracted and merged code blocks
        """
        # Step 1: Find all keyword matches with line numbers
        keyword_matches = self._find_keyword_matches(content, keywords)

        if not keyword_matches:
            return []

        # Step 2: For each match, find the enclosing code block
        raw_blocks = []
        for match in keyword_matches:
            block = self._find_enclosing_block(content, match)
            if block:
                raw_blocks.append(block)

        # Step 3: Merge overlapping or adjacent blocks
        merged_blocks = self._merge_blocks(raw_blocks)

        # Step 4: Create CodeBlock objects with metadata
        code_blocks = []
        for start_line, end_line, matched_keywords in merged_blocks:
            block_content = self._extract_block_content(
                content, start_line, end_line)
            code_block = CodeBlock(
                content=block_content,
                start_line=start_line,
                end_line=end_line,
                file_path=file_path,
                matched_keywords=matched_keywords,
            )
            code_blocks.append(code_block)

        # Step 5: Validate block sizes and emit warnings
        self._validate_block_sizes(code_blocks)

        return code_blocks

    def _find_keyword_matches(
        self, content: str, keywords: List[str]
    ) -> List[Tuple[int, str]]:
        """
        Find all lines containing upgrade keywords.

        Args:
            content: File content to search
            keywords: List of regex patterns

        Returns:
            List of(line_number, matched_keyword) tuples
        """
        matches = []
        lines = content.splitlines()

        # For each line in the file
        for line_num, line in enumerate(lines, 1):
            # Check each keyword pattern
            for keyword in keywords:
                if re.search(keyword, line):
                    matches.append((line_num, keyword))
                    # Don't match multiple keywords on same line to avoid duplicates
                    break

        return matches

    def _find_enclosing_block(
        self, content: str, match: Tuple[int, str]
    ) -> Tuple[int, int, str]:
        """
        Find the smallest enclosing code block for a keyword match.

        Args:
            content: File content
            match: (line_number, keyword) tuple

        Returns:
            (start_line, end_line, keyword) tuple or None if no block found
        """
        line_num, keyword = match
        lines = content.splitlines()

        # Step 1: Start from the matched line and scan backwards for opening brace
        # Look for patterns like: if (...) {, method() {, class Name {
        start_line = self._find_block_start(lines, line_num)

        # Step 2: From the opening brace, find the matching closing brace
        # Handle nested braces correctly
        end_line = self._find_block_end(lines, start_line)

        # Step 3: Validate we found a complete block
        if start_line and end_line and start_line < end_line:
            return (start_line, end_line, keyword)

        # Fallback: return just the matched line if no block found
        return (line_num, line_num, keyword)

    def _find_block_start(self, lines: List[str], line_num: int) -> int:
        """
        Find the start of the code block containing the given line.

        Args:
            lines: List of file lines
            line_num: Line number to start search from (1-indexed)

        Returns:
            Line number of block start, or original line_num if not found
        """
        # Step 1: Start from current line and scan backwards
        for i in range(line_num - 1, -1, -1):  # Convert to 0-indexed
            line = lines[i].strip()

            # Step 2: Look for opening brace patterns
            # - Method/class declarations: ") {", "} {", "class X {"
            # - Control structures: "if (...) {", "for (...) {", etc.
            if re.search(r"[{]\s*$", line):  # Line ends with opening brace
                return i + 1  # Convert back to 1-indexed

            # Step 3: Stop if we hit certain boundary patterns
            # - Another closing brace (end of previous block)
            # - Package/import statements
            # - Class-level annotations
            if re.search(r"[}]\s*$|^package\s|^import\s|^@\w+", line):
                break

        # Step 4: If no opening brace found, return original line
        return line_num

    def _find_block_end(self, lines: List[str], start_line: int) -> int:
        """
        Find the end of the code block starting at the given line.

        Args:
            lines: List of file lines
            start_line: Line number where block starts(1-indexed)

        Returns:
            Line number of block end, or start_line if not found
        """
        # Step 1: Count braces to find matching closing brace
        brace_count = 0
        found_opening = False

        # Step 2: Start from the start line and scan forward
        for i in range(start_line - 1, len(lines)):  # Convert to 0-indexed
            line = lines[i]

            # Step 3: Count opening and closing braces
            # Handle braces in strings/comments by simple heuristic
            if not self._is_in_string_or_comment(line):
                brace_count += line.count("{")
                brace_count -= line.count("}")

                # Mark that we've seen at least one opening brace
                if "{" in line:
                    found_opening = True

                # Step 4: When brace count returns to 0, we found the end
                if found_opening and brace_count == 0:
                    return i + 1  # Convert back to 1-indexed

        # Step 5: If no matching brace found, return start line
        return start_line

    def _is_in_string_or_comment(self, line: str) -> bool:
        """
        Simple heuristic to check if braces are in strings or comments.

        Args:
            line: Line of code to check

        Returns:
            True if line appears to be mostly string/comment content
        """
        # Step 1: Remove string literals (simple approach)
        # This is not perfect but good enough for most cases
        line_no_strings = re.sub(r'"[^"]*"', "", line)
        line_no_strings = re.sub(r"'[^']*'", "", line_no_strings)

        # Step 2: Check if remaining line starts with comment
        stripped = line_no_strings.strip()
        if stripped.startswith("//") or stripped.startswith("/*"):
            return True

        # Step 3: Simple heuristic - if most braces were removed, probably in strings
        original_braces = line.count("{") + line.count("}")
        remaining_braces = line_no_strings.count(
            "{") + line_no_strings.count("}")

        return original_braces > 0 and remaining_braces == 0

    def _merge_blocks(
        self, blocks: List[Tuple[int, int, str]]
    ) -> List[Tuple[int, int, List[str]]]:
        """
        Merge overlapping or adjacent code blocks.

        Args:
            blocks: List of(start_line, end_line, keyword) tuples

        Returns:
            List of(start_line, end_line, keywords_list) tuples
        """
        if not blocks:
            return []

        if len(blocks) == 1:
            start, end, keyword = blocks[0]
            return [(start, end, [keyword])]

        # Step 1: Sort blocks by start line
        sorted_blocks = sorted(blocks, key=lambda x: x[0])

        # Step 2: Merge overlapping/adjacent blocks
        merged = []
        current_start, current_end, current_keyword = sorted_blocks[0]
        current_keywords = [current_keyword]

        for start, end, keyword in sorted_blocks[1:]:
            # Step 3: Check if blocks overlap or are adjacent (within 2 lines)
            if start <= current_end + 2:
                # Merge: extend current block and combine keywords
                current_end = max(current_end, end)
                if keyword not in current_keywords:
                    current_keywords.append(keyword)
            else:
                # No overlap: save current and start new block
                merged.append((current_start, current_end, current_keywords))
                current_start, current_end = start, end
                current_keywords = [keyword]

        # Step 4: Add the last block
        merged.append((current_start, current_end, current_keywords))

        return merged

    def _extract_block_content(
        self, content: str, start_line: int, end_line: int
    ) -> str:
        """
        Extract the actual content of a code block.

        Args:
            content: Full file content
            start_line: Start line number(1-indexed)
            end_line: End line number(1-indexed, inclusive)

        Returns:
            Code block content as string
        """
        lines = content.splitlines()

        # Step 1: Extract the relevant lines (convert to 0-indexed)
        block_lines = lines[start_line - 1: end_line]

        # Step 2: Preserve original indentation
        return "\n".join(block_lines)

    def _validate_block_sizes(self, blocks: List[CodeBlock]) -> None:
        """
        Validate block sizes and emit warnings for large blocks.

        Args:
            blocks: List of extracted code blocks
        """
        for block in blocks:
            # Step 1: Check if block exceeds size threshold
            if block.line_count > self.max_block_lines:
                # Step 2: Emit warning (non-blocking)
                self.console.print(
                    f"⚠️  Large code block detected in {block.file_path}",
                    style="yellow")
                self.console.print(
                    f"   Lines {block.start_line}-{block.end_line} ({block.line_count} lines)",
                    style="yellow")
                self.console.print(
                    f"   Keywords: {', '.join(block.matched_keywords)}",
                    style="yellow")
                self.console.print(
                    f"   Consider adjusting keywords or block extraction logic",
                    style="yellow")
                self.console.print()  # Empty line for readability
