import re
from typing import List, Optional, Tuple
from rich.console import Console


class CodeMatcher:
    """
    Handles content-based matching for applying code changes when line numbers
    are unreliable (the best available LLM at the time of writing is VERY
    unreliable).

    This class provides fuzzy matching capabilities to find code patterns in files,
    handling whitespace variations and indentation differences.
    """

    def __init__(self, console: Optional[Console] = None):
        """Initialize CodeMatcher with optional console for debugging output."""
        self.console = console or Console()

    def find_content_match(self, file_lines: List[str], target_content: str) -> Optional[Tuple[int, int]]:
        """
        Find where target_content matches in the file lines.

        Args:
            file_lines: List of file lines (with or without line endings)
            target_content: Content to find in the file

        Returns:
            (start_idx, end_idx) tuple if found, None otherwise
            Indices are 0-based for direct list slicing
        """
        if not target_content.strip():
            return None

        target_lines = [
            self._normalize_line(line) for line in target_content.splitlines()
            if line.strip()
        ]

        normalized_file_lines = [
            self._normalize_line(line) for line in file_lines
        ]

        exact_match = self._find_exact_match(
            normalized_file_lines, target_lines, target_content)
        if exact_match:
            return exact_match

        # Fallback to fuzzy matching
        return self._find_fuzzy_match(normalized_file_lines, target_lines)

    def _normalize_line(self, line: str) -> str:
        """Normalize a single line for comparison."""
        return line.rstrip('\n\r').rstrip()

    def _find_exact_match(self, file_lines: List[str], target_lines: List[str],
                          original_target: str) -> Optional[Tuple[int, int]]:
        """
        Find exact content match with whitespace normalization.

        Args:
            file_lines: Normalized file lines
            target_lines: Normalized target lines (non-empty only)
            original_target: Original target content for length calculation

        Returns:
            (start_idx, end_idx) if exact match found
        """
        if not target_lines:
            return None

        # Try to find a contiguous match
        for start_idx in range(len(file_lines) - len(target_lines) + 1):
            if self._lines_match_at_position(file_lines, target_lines, start_idx):
                # Calculate end index including original empty lines
                end_idx = self._calculate_end_index(
                    start_idx, len(target_lines), original_target)
                end_idx = min(end_idx, len(file_lines))
                return (start_idx, end_idx)

        return None

    def _lines_match_at_position(self, file_lines: List[str], target_lines: List[str],
                                 start_idx: int) -> bool:
        """
        Check if target lines match file lines starting at given position.

        Args:
            file_lines: File lines to check against
            target_lines: Target lines to match
            start_idx: Starting position in file_lines

        Returns:
            True if all target lines match starting at start_idx
        """
        for i, target_line in enumerate(target_lines):
            if start_idx + i >= len(file_lines):
                return False

            file_line = file_lines[start_idx + i]
            if not self._single_line_match(file_line, target_line):
                return False

        return True

    def _single_line_match(self, file_line: str, target_line: str) -> bool:
        """
        Check if two lines match with whitespace tolerance.

        Args:
            file_line: Line from file
            target_line: Line from target content

        Returns:
            True if lines match (with whitespace normalization)
        """
        # Strategy 1: Remove all whitespace and compare
        file_normalized = ''.join(file_line.split())
        target_normalized = ''.join(target_line.split())

        if file_normalized == target_normalized:
            return True

        # Strategy 2: Trim whitespace but preserve internal spacing
        if file_line.strip() == target_line.strip():
            return True

        # Strategy 3: Normalize common whitespace patterns
        file_clean = re.sub(r'\s+', ' ', file_line.strip())
        target_clean = re.sub(r'\s+', ' ', target_line.strip())

        return file_clean == target_clean

    def _calculate_end_index(self, start_idx: int, matched_lines: int, original_target: str) -> int:
        """
        Calculate the proper end index including any trailing empty lines from original target.

        Args:
            start_idx: Starting index of the match
            matched_lines: Number of non-empty lines that matched
            original_target: Original target content to check for empty lines

        Returns:
            End index for slicing
        """
        base_end = start_idx + matched_lines

        # Check if original target had trailing empty lines
        original_lines = original_target.splitlines()
        if len(original_lines) > matched_lines:
            # Add the difference (empty lines at the end)
            extra_lines = len(original_lines) - matched_lines
            return base_end + extra_lines

        return base_end

    def _find_fuzzy_match(self, file_lines: List[str], target_lines: List[str]
                          ) -> Optional[Tuple[int, int]]:
        """
        Find content using fuzzy matching based on key identifiers.

        Args:
            file_lines: File lines to search in
            target_lines: Target lines to find

        Returns:
            (start_idx, end_idx) if fuzzy match found with sufficient confidence
        """
        if not target_lines:
            return None

        # Extract key patterns from target content
        key_patterns = self._extract_key_patterns(target_lines)
        if not key_patterns:
            return None

        # Find best matching section
        best_match = None
        best_score = 0
        # At least 70% match or minimum 2 patterns
        threshold = max(len(key_patterns) * 0.7, 2)

        for start_idx in range(len(file_lines) - len(target_lines) + 1):
            end_idx = start_idx + len(target_lines)
            section_content = ' '.join(file_lines[start_idx:end_idx])

            score = sum(
                1 for pattern in key_patterns if pattern in section_content)

            if score > best_score and score >= threshold:
                best_score = score
                best_match = (start_idx, end_idx)

        if best_match:
            self.console.print(
                f"🔍 Fuzzy match found with {best_score}/{len(key_patterns)} patterns",
                style="yellow")

        return best_match

    def _extract_key_patterns(self, target_lines: List[str]) -> List[str]:
        """
        Extract key identifiers and patterns from target lines for fuzzy matching.

        Args:
            target_lines: Lines to extract patterns from

        Returns:
            List of key patterns/identifiers
        """
        key_patterns = []

        for line in target_lines:
            # Extract meaningful identifiers (alphanumeric sequences)
            identifiers = re.findall(r'\w+', line)
            key_patterns.extend(identifiers)

            # Extract quoted strings
            quoted_strings = re.findall(r'["\']([^"\']+)["\']', line)
            key_patterns.extend(quoted_strings)

            # Extract version numbers or specific values
            versions = re.findall(r'\d+\.\d+(?:\.\d+)?', line)
            key_patterns.extend(versions)

        # Remove common/generic words that aren't helpful for matching
        generic_words = {
            'the', 'and', 'or', 'if', 'then', 'else', 'for', 'while', 'do', 'return',
            'public', 'private', 'static', 'final', 'class', 'import', 'package'
        }

        filtered_patterns = [
            p for p in key_patterns if p.lower() not in generic_words and len(p) > 1]
        return list(set(filtered_patterns))

    def debug_match_attempt(self, file_lines: List[str], target_content: str
                            ) -> None:
        """
        Debug helper to show why a match might be failing.

        Args:
            file_lines: File lines being searched
            target_content: Content trying to match
        """
        self.console.print("\n🔍 Debug: Match Analysis", style="bold yellow")

        target_lines = self._normalize_line(target_content)
        key_patterns = self._extract_key_patterns(target_lines)

        self.console.print(f"Target lines ({len(target_lines)}):")
        for i, line in enumerate(target_lines):
            self.console.print(f"  {i+1}: {repr(line)}")

        self.console.print(f"\nKey patterns: {key_patterns}")

        self.console.print(f"\nFile has {len(file_lines)} lines")

        # Show first few lines of file for context
        self.console.print("File preview:")
        for i, line in enumerate(file_lines[:10]):
            if len(target_lines) == 1:
                self.console.print(f"  {i+1}: {line}")
            else:
                self.console.print(f"  {i+1}: {repr(line)}")

        if len(file_lines) > 10:
            self.console.print(f"  ... and {len(file_lines) - 10} more lines")
            self.console.print(f"  ... and {len(file_lines) - 10} more lines")

    def preserve_indentation(self, new_content: str,
                             base_indentation: str = None,
                             original_lines: List[str] = None,
                             start_idx: int = None, end_idx: int = None
                             ) -> List[str]:
        """
        Apply base indentation to new content.

        Args:
            new_content: Content to apply
            base_indentation: Base indentation string (for inserts)
            original_lines: Original file lines (for updates)
            start_idx: Start index where content was matched (for updates)
            end_idx: End index where content was matched (for updates)

        Returns:
            List of new lines with preserved indentation
        """
        if not new_content.strip():
            return []

        new_lines = new_content.splitlines()
        if not new_lines:
            return []

        if base_indentation is not None:
            # For inserts - use provided base indentation
            base_indent = base_indentation
        elif (original_lines is not None
              and start_idx is not None
              and end_idx is not None):
            # For updates - extract from original lines

            # Single line optimization
            if end_idx - start_idx == 1 and len(new_lines) == 1:
                original_line = original_lines[start_idx].rstrip('\n\r')
                original_indent = len(original_line) - \
                    len(original_line.lstrip())
                indent_str = original_line[:original_indent]
                new_line = indent_str + new_lines[0].strip() + '\n'
                return [new_line]

            # Multi-line - extract base indentation
            original_section = original_lines[start_idx:end_idx]
            base_indent = self._extract_base_indentation(original_section)
        else:
            base_indent = ""

        result_lines = []
        base_indent_len = len(base_indent)

        for line in new_lines:
            if line.strip():  # Non-empty line
                line_indent = len(line) - len(line.lstrip())

                # Check if line already has correct base indentation
                if line_indent >= base_indent_len and line.startswith(base_indent):
                    preserved_line = line
                elif line_indent > 0:
                    preserved_line = base_indent + line
                else:
                    preserved_line = base_indent + line.strip()
            else:
                preserved_line = line

            if not preserved_line.endswith('\n'):
                preserved_line += '\n'
            result_lines.append(preserved_line)

        return result_lines

    def _extract_base_indentation(self, original_lines: List[str]) -> str:
        """
        Extract the base indentation from the original matched lines.

        Args:
            original_lines: Original lines that were matched

        Returns:
            Base indentation string (spaces/tabs)
        """
        if not original_lines:
            return ""

        indentations = []
        for line in original_lines:
            if line.strip():  # Non-empty line
                line_content = line.rstrip('\n\r')
                indentation = len(line_content) - len(line_content.lstrip())
                indentations.append(indentation)

        if not indentations:
            return ""

        min_indent = min(indentations)

        for line in original_lines:
            if line.strip():
                line_content = line.rstrip('\n\r')
                return line_content[:min_indent]

        return ""
