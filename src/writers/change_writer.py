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

        all_changes.sort(
            key=lambda change: change.location.start_line, reverse=True)

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
        if auto_approve:
            self._apply_changes(file_path, all_changes)
        else:
            self._interactive_change_selection(file_path, all_changes)

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

    def _apply_changes(self, file_path: str, changes: List):
        """Apply selected changes to a file."""
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()

            for change in changes:
                if change.change_type == "update":
                    start_idx = change.location.start_line - 1  # Convert to 0-indexed
                    end_idx = change.location.end_line  # end_line is inclusive

                    new_lines = change.after.splitlines(keepends=True)
                    lines[start_idx:end_idx] = new_lines

                elif change.change_type == "insert":
                    insert_idx = change.location.start_line - 1
                    new_lines = change.after.splitlines(keepends=True)
                    lines[insert_idx:insert_idx] = new_lines

                elif change.change_type == "delete":
                    start_idx = change.location.start_line - 1
                    end_idx = change.location.end_line
                    del lines[start_idx:end_idx]

            with open(file_path, 'w') as f:
                f.writelines(lines)

        except Exception as e:
            self.console.print(f"❌ Failed to apply changes: {e}", style="red")
