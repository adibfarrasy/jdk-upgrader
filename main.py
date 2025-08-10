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
from src.upgraders.upgrade_pipeline import UpgradePipeline
from src.writers.change_writer import ChangeWriter

console = Console()


@click.command()
@click.argument("repo_path", type=click.Path(exists=True, path_type=Path))
@click.option("--dry-run", is_flag=True, help="Show changes without applying")
@click.option(
    "--auto-approve", is_flag=True, help="Apply all changes without prompting"
)
def main(repo_path: Path, dry_run: bool, auto_approve: bool):
    """Upgrade Java projects to target JDK."""

    console.print(Panel.fit("🚀 JDK Upgrader", padding=(
        2, 5), style="bold blue"))

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

    pipeline = UpgradePipeline(llm, console)
    responses = pipeline.analyze_repository(repo_path)

    writer = ChangeWriter(console)
    writer.process_responses(responses, dry_run, auto_approve)

    console.print("✅ Analysis complete!", style="bold green")

if __name__ == "__main__":
    main()
