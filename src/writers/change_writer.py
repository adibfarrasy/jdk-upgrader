from typing import Dict, List
from rich.console import Console
from rich.prompt import Confirm

from src.models.response import StructuredResponse


class ChangeWriter:
    """Writes upgrade changes to files based on StructuredResponse objects."""

    def __init__(self, console=None):
        """Initialize change writer."""
        self.console = console or Console()

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
            self._apply_all_changes_batch(file_path, all_changes)
        else:
            self._apply_changes_interactively(file_path, all_changes)

    def _interactive_change_selection(self, file_path: str, changes: List):
        """Let user select which changes to apply individually."""
        selected_changes = []

        for i, change in enumerate(changes, 1):
            self.console.print(f"\n[bold]Change {i} of {len(changes)}:[/bold]")
            self.console.print(str(change), markup=True)

            if Confirm.ask("Apply this change?"):
                selected_changes.append(change)

        if selected_changes:
            self._apply_changes(file_path, selected_changes)
            self.console.print(
                f"✅ Applied {len(selected_changes)} changes", style="green")
        else:
            self.console.print("⏭️  No changes applied", style="yellow")

    def _apply_changes_interactively(self, file_path: str, changes: List):
        """Apply changes one by one with user confirmation."""
        applied_count = 0
        skipped_count = 0

        for i, change in enumerate(changes, 1):
            self.console.print(
                f"\n[bold]Change {i} of {len(changes)}:[/bold]")
            self.console.print(str(change), markup=True)

            if Confirm.ask("Apply this change?"):
                success = self._apply_single_change(file_path, change)
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

    def _apply_all_changes_batch(self, file_path: str, changes: List):
        """Apply all changes in batch mode (auto-approve)."""

        applied_count = 0
        for change in changes:
            success = self._apply_single_change(file_path, change)
            if success:
                applied_count += 1

        self.console.print(f"✅ Applied {applied_count} changes", style="green")

    def _apply_single_change(self, file_path: str, change) -> bool:
        """Apply a single change to the file immediately."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            lines = content.splitlines(keepends=True)

            if not self._validate_change_bounds(change, len(lines)):
                self.console.print(
                    f"⚠️ Change out of bounds: line {change.location.start_line}", style="yellow")
                return False

            start_idx = change.location.start_line - 1
            end_idx = change.location.end_line

            if change.change_type == "update":
                # Verify content matches
                actual_content = ''.join(lines[start_idx:end_idx]).rstrip('\n')
                expected_content = change.before.rstrip('\n')

                if actual_content != expected_content:
                    self.console.print(
                        f"⚠️ Content mismatch at line {change.location.start_line}", style="yellow")
                    self.console.print(
                        f"Expected: {repr(expected_content)}", style="dim")
                    self.console.print(
                        f"Actual:   {repr(actual_content)}", style="dim")
                    return False

                after_content = change.after
                if not after_content.endswith('\n'):
                    after_content += '\n'

                new_lines = after_content.splitlines(keepends=True)
                lines[start_idx:end_idx] = new_lines

            elif change.change_type == "insert":
                after_content = change.after
                if not after_content.endswith('\n'):
                    after_content += '\n'

                new_lines = after_content.splitlines(keepends=True)
                lines[start_idx:start_idx] = new_lines

            elif change.change_type == "delete":
                del lines[start_idx:end_idx]

            with open(file_path, 'w') as f:
                f.writelines(lines)

            return True

        except Exception as e:
            self.console.print(f"❌ Error applying change: {e}", style="red")
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
