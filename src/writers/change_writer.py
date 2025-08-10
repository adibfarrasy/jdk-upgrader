from typing import List
from rich.console import Console
from rich.prompt import Confirm

from src.models.response import StructuredResponse
from src.utils.code_matcher import CodeMatcher


class ChangeWriter:
    """Writes upgrade changes to files based on StructuredResponse objects."""

    def __init__(self, console=None):
        """Initialize change writer."""
        self.console = console or Console()
        self.code_matcher = CodeMatcher(self.console)

    def process_responses(self, responses: List[StructuredResponse],
                          dry_run: bool, auto_approve: bool):
        """Process all upgrade responses and write changes to files."""
        if not responses:
            self.console.print("No changes suggested", style="yellow")
            return

        for response in responses:
            if response.changes:
                file_path = response.changes[0].location.file_path
                self._process_file_responses(
                    file_path, [response], dry_run, auto_approve)

    def _process_file_responses(self, file_path: str,
                                responses: List[StructuredResponse],
                                dry_run: bool, auto_approve: bool):
        """Process all responses for a single file."""
        self.console.print(f"\n📄 [bold]{file_path}[/bold]")

        all_changes = []
        for response in responses:
            all_changes.extend(response.changes)

        all_changes = sorted(all_changes,
                             key=lambda c: c.location.start_line, reverse=True)

        if not all_changes:
            self.console.print(
                "No changes found for this file", style="yellow")
            return

        if dry_run:
            # Show all changes in dry run
            for i, change in enumerate(all_changes, 1):
                self.console.print(f"\n[bold]Change {i}:[/bold]")
                self.console.print(str(change), markup=True)
            self.console.print(
                "🔍 [yellow]Dry run - no changes applied[/yellow]")
            return
        elif auto_approve:
            self._apply_all_changes_batch(file_path, all_changes, True)
        else:
            self._apply_changes_interactively(file_path, all_changes, False)

    def _apply_changes_interactively(self, file_path: str, changes: List, auto_approve: bool):
        """Apply changes one by one with user confirmation."""
        applied_count = 0
        skipped_count = 0

        for i, change in enumerate(changes, 1):
            self.console.print(
                f"\n[bold]Change {i} of {len(changes)}:[/bold]")
            self.console.print(str(change), markup=True)

            if Confirm.ask("Apply this change?"):
                success = self._apply_single_change(
                    file_path, change, auto_approve)
                if success:
                    applied_count += 1
                    self.console.print(
                        "✅ Applied successfully", style="green")
                else:
                    skipped_count += 1
                    self.console.print("❌ Failed to apply", style="red")
            else:
                skipped_count += 1
                self.console.print("⏭️ Skipped", style="yellow")

    def _apply_all_changes_batch(self, file_path: str, changes: List, auto_approve):
        """Apply all changes in batch mode (auto-approve)."""
        applied_count = 0
        for change in changes:
            success = self._apply_single_change(
                file_path, change, auto_approve)
            if success:
                applied_count += 1

        self.console.print(f"✅ Applied {applied_count} changes", style="green")

    def _apply_single_change(self, file_path: str, change, auto_approve: bool) -> bool:
        """
        Apply a single change to the file.
        Try line number approach first, then fallback to content matching.
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            lines = content.splitlines(keepends=True)

            if change.change_type == "insert":
                return self._apply_insert_by_line_number(file_path, lines, change)

            # For updates and deletes, try line number first, then content matching
            if change.change_type in ["update", "delete"]:
                if self._try_line_number_approach(file_path, lines, change):
                    return True

                return self._apply_by_content_matching(file_path, lines, change, auto_approve)

            return False

        except Exception as e:
            self.console.print(f"❌ Error applying change: {e}", style="red")
            return False

    def _apply_insert_by_line_number(self, file_path: str, lines: List[str], change) -> bool:
        """Apply insert change using line number."""
        if not self._validate_change_bounds(change, len(lines)):
            self.console.print(
                f"⚠️ Insert out of bounds: line {change.location.start_line}", style="yellow")
            return False

        start_idx = change.location.start_line - 1
        after_content = change.after
        if not after_content.endswith('\n'):
            after_content += '\n'

        base_indentation = self._detect_insert_indentation(lines, start_idx)
        new_lines = self.code_matcher.preserve_indentation(
            change.after, base_indentation)

        lines[start_idx:start_idx] = new_lines

        return self._write_file(file_path, lines)

    def _detect_insert_indentation(self, lines: List[str], insert_idx: int) -> str:
        indent_counts = {}

        for offset in range(-2, 3):  # Check 5 nearby lines
            line_idx = insert_idx + offset
            if 0 <= line_idx < len(lines):
                line = lines[line_idx].rstrip('\n\r')
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    indent_counts[indent] = indent_counts.get(indent, 0) + 1

        # Use most common indentation
        if indent_counts:
            most_common_indent = max(
                indent_counts.items(), key=lambda x: x[1])[0]
            for offset in range(-2, 3):
                line_idx = insert_idx + offset
                if 0 <= line_idx < len(lines):
                    line = lines[line_idx].rstrip('\n\r')
                    if line.strip() and len(line) - len(line.lstrip()) == most_common_indent:
                        return line[:most_common_indent]

        return ""

    def _try_line_number_approach(self, file_path: str, lines: List[str], change) -> bool:
        """Try to apply change using LLM-suggested line numbers."""
        if not self._validate_change_bounds(change, len(lines)):
            return False

        start_idx = change.location.start_line - 1
        end_idx = change.location.end_line

        # Verify content matches at suggested location
        actual_content = ''.join(lines[start_idx:end_idx]).rstrip('\n')
        expected_content = change.before.rstrip('\n')

        if actual_content == expected_content:
            # Exact match - apply the change
            if change.change_type == "update":
                new_lines = self.code_matcher.preserve_indentation(
                    change.after, original_lines=lines, start_idx=start_idx,
                    end_idx=end_idx)
                lines[start_idx:end_idx] = new_lines

            elif change.change_type == "delete":
                del lines[start_idx:end_idx]

            return self._write_file(file_path, lines)

        return False

    def _apply_by_content_matching(self, file_path: str, lines: List[str], change, auto_approve: bool) -> bool:
        """Apply change using content pattern matching."""
        match_result = self.code_matcher.find_content_match(
            lines, change.before)

        if not match_result:
            self.console.print("Content not found in file", style="yellow")
            self.console.print(
                f"Looking for: {repr(change.before[:100])}...", style="dim")

            # Optional: show debug info
            if self.console.is_terminal and not auto_approve:
                if Confirm.ask("Show debug info for this match?", default=False):
                    self.code_matcher.debug_match_attempt(lines, change.before)

            return False

        start_idx, end_idx = match_result

        if change.change_type == "update":
            new_lines = self.code_matcher.preserve_indentation(
                change.after, original_lines=lines, start_idx=start_idx,
                end_idx=end_idx)
            lines[start_idx:end_idx] = new_lines

        elif change.change_type == "delete":
            del lines[start_idx:end_idx]

        self.console.print(
            f"✅ Applied using content matching (lines {start_idx+1}-{end_idx})",
            style="green")

        return self._write_file(file_path, lines)

    def _write_file(self, file_path: str, lines: List[str]) -> bool:
        """Write lines back to file."""
        try:
            with open(file_path, 'w') as f:
                f.writelines(lines)
            return True
        except Exception as e:
            self.console.print(f"❌ Error writing file: {e}", style="red")
            return False

    def _validate_change_bounds(self, change, total_lines):
        """Validate that change line numbers are within file bounds."""
        if change.location.start_line < 1 or change.location.start_line > total_lines:
            return False
        if change.location.end_line < 1 or change.location.end_line > total_lines:
            return False
        if change.location.start_line > change.location.end_line:
            return False
        return True
