#!/usr/bin/env python3
import click
from pathlib import Path
from rich.console import Console
from rich.progress import track
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm

from langchain_openai import AzureChatOpenAI
from config import Config
# from src.analyzers.gradle_analyzer import GradleAnalyzer
# from src.analyzers.ci_analyzer import CIAnalyzer

console = Console()


@click.command()
@click.argument("repo_path", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Show changes without applying")
@click.option(
    "--auto-approve", is_flag=True, help="Apply all changes without prompting"
)
def main(repo_path: Path, dry_run: bool, auto_approve: bool):
    """Upgrade Java projects to JDK 21."""

    console.print(Panel.fit("🚀 JDK 21 Upgrader", style="bold blue"))

    # Validate and initialize
    try:
        Config.validate()
        llm = AzureChatOpenAI(
            azure_endpoint=Config.AZURE_ENDPOINT,
            azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
            api_version=Config.AZURE_API_VERSION,
            temperature=Config.TEMPERATURE,
        )
    except ValueError as e:
        console.print(f"❌ {e}", style="bold red")
        raise click.Abort()

    gradle_analyzer = GradleAnalyzer(llm)
    ci_analyzer = CIAnalyzer(llm)

    # Process files
    process_files(repo_path, gradle_analyzer, ci_analyzer, dry_run, auto_approve)

    console.print("✅ Analysis complete!", style="bold green")


def process_files(repo_path, gradle_analyzer, ci_analyzer, dry_run, auto_approve):
    # Find all files to process
    all_files = []
    for pattern in Config.BUILD_FILES + Config.CI_FILES:
        all_files.extend(repo_path.glob(pattern))

    if not all_files:
        console.print("No build or CI files found", style="yellow")
        return

    # Process with progress bar
    for file_path in track(all_files, description="Analyzing files..."):
        analyzer = gradle_analyzer if file_path.suffix in [".gradle"] else ci_analyzer

        with open(file_path, "r") as f:
            content = f.read()

        suggestions = analyzer.analyze(content)
        if suggestions:
            show_and_apply_changes(
                file_path, content, suggestions, dry_run, auto_approve
            )


def show_and_apply_changes(
    file_path, original_content, suggestions, dry_run, auto_approve
):
    console.print(f"\n📄 [bold]{file_path}[/bold]")

    # Show diff with syntax highlighting
    syntax = Syntax(suggestions, "gradle", theme="monokai", line_numbers=True)
    console.print(Panel(syntax, title="Proposed Changes"))

    if dry_run:
        console.print("🔍 [yellow]Dry run - no changes applied[/yellow]")
        return

    # Get approval
    if auto_approve or Confirm.ask("Apply these changes?"):
        try:
            with open(file_path, "w") as f:
                f.write(suggestions)
            console.print("✅ Changes applied", style="green")
        except Exception as e:
            console.print(f"❌ Failed to write file: {e}", style="red")
    else:
        console.print("⏭️  Skipped", style="yellow")


if __name__ == "__main__":
    main()
