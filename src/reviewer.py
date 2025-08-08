from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm, Prompt
from rich.diff import Diff


class HumanReviewer:
    """Handles human-in-the-loop review of suggested changes."""

    def __init__(self):
        """Initialize the reviewer with Rich console."""
        self.console = Console()

    def review_and_apply(self, file_path: Path, suggestions: str) -> bool:
        """
        Show changes to human and get approval to apply.

        TODO:
        1. Read current file content
        2. Show side-by-side diff of current vs suggested
        3. Highlight syntax with appropriate language detection
        4. Present clear options (apply/skip/edit/quit)
        5. Handle edit option - allow inline modifications
        6. Apply changes only after explicit approval
        7. Show confirmation of what was applied
        8. Handle file backup before applying changes
        9. Support undo/rollback of recent changes
        10. Track and summarize all changes made in session

        Args:
            file_path: Path to file being reviewed
            suggestions: LLM-generated suggested content

        Returns:
            True if changes were applied, False if skipped
        """
        # TODO: Implement full review workflow
        self._show_file_header(file_path)
        self._show_diff(file_path, suggestions)

        choice = self._get_user_choice()

        if choice == "apply":
            return self._apply_changes(file_path, suggestions)
        elif choice == "edit":
            return self._edit_and_apply(file_path, suggestions)
        else:
            self.console.print("⏭️  Skipped", style="yellow")
            return False

    def _show_file_header(self, file_path: Path):
        """Display file being reviewed."""
        # TODO: Add file stats (size, last modified, etc.)
        self.console.print(f"\n📄 [bold blue]{file_path}[/bold blue]")

    def _show_diff(self, file_path: Path, suggestions: str):
        """Show diff between current and suggested content."""
        # TODO: Implement proper diff visualization
        try:
            with open(file_path, "r") as f:
                current_content = f.read()

            # Use Rich Syntax for highlighting
            syntax = Syntax(
                suggestions,
                self._detect_language(file_path),
                theme="monokai",
                line_numbers=True,
            )
            self.console.print(Panel(syntax, title="Suggested Changes"))

        except Exception as e:
            self.console.print(f"❌ Error reading file: {e}", style="red")

    def _detect_language(self, file_path: Path) -> str:
        """Detect syntax highlighting language from file extension."""
        # TODO: Expand language detection
        ext_map = {
            ".gradle": "groovy",
            ".java": "java",
            ".groovy": "groovy",
            ".yml": "yaml",
            ".yaml": "yaml",
            ".py": "python",
        }
        return ext_map.get(file_path.suffix, "text")

    def _get_user_choice(self) -> str:
        """Get user's choice for how to handle the suggestion."""
        # TODO: Add more options (view original, compare side-by-side)
        choices = ["apply", "skip", "edit", "quit"]
        choice = Prompt.ask("Action", choices=choices, default="apply")

        if choice == "quit":
            raise KeyboardInterrupt("User requested quit")

        return choice

    def _apply_changes(self, file_path: Path, content: str) -> bool:
        """Apply suggested changes to file."""
        # TODO: Add backup functionality
        try:
            with open(file_path, "w") as f:
                f.write(content)
            self.console.print("✅ Changes applied", style="green")
            return True
        except Exception as e:
            self.console.print(f"❌ Failed to apply: {e}", style="red")
            return False

    def _edit_and_apply(self, file_path: Path, suggestions: str) -> bool:
        """Allow user to edit suggestions before applying."""
        # TODO: Implement interactive editing
        # Could use temporary file + editor, or rich text input
        self.console.print("🚧 Edit mode not implemented yet", style="yellow")
        return False
