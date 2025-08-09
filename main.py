#!/usr/bin/env python3
import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm
from rich.progress import Progress
from rich.markdown import Markdown
from langchain_openai import AzureChatOpenAI
from langchain.schema import HumanMessage

from config import Config
from src.analyzers.build_file_analyzer import BuildFileAnalyzer
from src.analyzers.ci_analyzer import CIAnalyzer

console = Console()


@click.command()
@click.argument("repo_path", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Show changes without applying")
@click.option(
    "--auto-approve", is_flag=True, help="Apply all changes without prompting"
)
def main(repo_path: Path, dry_run: bool, auto_approve: bool):
    """Upgrade Java projects to target JDK."""

    console.print(Panel.fit("🚀 JDK Upgrader", style="bold blue"))

    # Validate and initialize
    try:
        Config.validate()
        llm = AzureChatOpenAI(
            azure_endpoint=Config.AZURE_ENDPOINT,
            api_version=Config.AZURE_API_VERSION,
            api_key=Config.AZURE_OPENAI_API_KEY,
            azure_deployment=Config.AZURE_DEPLOYMENT_NAME,
            temperature=Config.TEMPERATURE,
        )
    except ValueError as e:
        console.print(f"❌ {e}", style="bold red")
        raise click.Abort()

    # TEST: LLM liveness / setup check
    # response = llm.invoke([
    #     HumanMessage(content="Hello, World! say something nice")
    # ])
    #
    # console.print(f"Response: {response.content}", style="bold green")

    build_file_analyzer = BuildFileAnalyzer(llm)
    ci_analyzer = CIAnalyzer(llm)

    process_files(repo_path, build_file_analyzer,
                  ci_analyzer, dry_run, auto_approve)

    console.print("✅ Analysis complete!", style="bold green")


def process_files(repo_path, build_file_analyzer, ci_analyzer, dry_run, auto_approve):
    all_files = []
    for pattern in Config.BUILD_FILES + Config.CI_FILES:
        all_files.extend(repo_path.glob(pattern))

    if not all_files:
        console.print("No build or CI files found", style="yellow")
        return

    results = []
   
    with Progress() as progress:
        task = progress.add_task("Analyzing files...", total=len(all_files))
        for file_path in all_files:
           analyzer = build_file_analyzer if file_path.suffix in [
               ".gradle", ".xml"
           ] else ci_analyzer
           with open(file_path, "r") as f:
               content = f.read()
           suggestions = analyzer.analyze(content, file_path)
           if suggestions:
               results.append((file_path, content, suggestions))
           progress.advance(task)
   
   # Now show results and prompt (progress bar is done)
    for file_path, content, suggestions in results:
        show_and_apply_changes(file_path, content, suggestions, dry_run, auto_approve)


def show_and_apply_changes(
    file_path, original_content, suggestions, dry_run, auto_approve
):
    console.print(f"\n📄 [bold]{file_path}[/bold]")

    console.print(str(suggestions), markup=True)

    if dry_run:
        console.print("🔍 [yellow]Dry run - no changes applied[/yellow]")
        return

    if auto_approve or Confirm.ask("Apply these changes?"):
        try:
            # TODO: use code extractor and only replace line contents
            # instead of re-writing the file
            # with open(file_path, "w") as f:
            #     f.write(suggestions)
            console.print("✅ Changes applied", style="green")
        except Exception as e:
            console.print(f"❌ Failed to write file: {e}", style="red")
    else:
        console.print("⏭️  Skipped", style="yellow")


if __name__ == "__main__":
    main()
