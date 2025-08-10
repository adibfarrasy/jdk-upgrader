from pathlib import Path
from typing import List
from rich.console import Console
from rich.progress import Progress, TextColumn,  TaskProgressColumn, TimeElapsedColumn

from config import Config
from src.models.response import StructuredResponse
from src.upgraders.build_upgrader import BuildUpgrader
from src.upgraders.ci_upgrader import CIUpgrader
from src.upgraders.config import UpgraderConfig
from src.upgraders.java_upgrader import JavaUpgrader
from src.upgraders.groovy_upgrader import GroovyUpgrader
from src.upgraders.kotlin_upgrader import KotlinUpgrader
from src.utils.code_extractor import CodeBlockExtractor


class UpgradePipeline:
    """Orchestrates JDK upgrade analysis across all file types."""

    def __init__(self, llm, console=None):
        self.build_upgrader = BuildUpgrader(llm)
        self.ci_upgrader = CIUpgrader(llm)
        self.java_upgrader = JavaUpgrader(llm)
        self.groovy_upgrader = GroovyUpgrader(llm)
        self.kotlin_upgrader = KotlinUpgrader(llm)
        self.code_extractor = CodeBlockExtractor(
            max_block_lines=UpgraderConfig.MAX_BLOCK_LINES, console=console)
        self.console = console or Console()

    def analyze_repository(self, repo_path: Path) -> List[StructuredResponse]:
        """Analyze repository for JDK upgrade opportunities."""
        all_responses = []

        # Collect all files by type
        build_files = self._collect_files(repo_path, Config.BUILD_FILES)
        ci_files = self._collect_files(repo_path, Config.CI_FILES)
        source_files = self._collect_files(repo_path, Config.SOURCE_FILES)

        total_files = len(build_files) + len(ci_files) + len(source_files)

        with Progress(
            TextColumn("{task.description}\n"),
            TaskProgressColumn(),
            TimeElapsedColumn(),
        ) as progress:
            task = progress.add_task("Analyzing files...", total=total_files)

            for file_path in build_files:
                relative_path = file_path.relative_to(repo_path)
                progress.update(
                    task, description=f"Analyzing {relative_path}...")
                response = self._analyze_build_file(file_path)
                if response and response.changes:
                    all_responses.append(response)
                progress.advance(task)

            for file_path in ci_files:
                relative_path = file_path.relative_to(repo_path)
                progress.update(
                    task, description=f"Analyzing {relative_path}...")
                response = self._analyze_ci_file(file_path)
                if response and response.changes:
                    all_responses.append(response)
                progress.advance(task)

            for file_path in source_files:
                relative_path = file_path.relative_to(repo_path)
                progress.update(
                    task, description=f"Analyzing {relative_path}...")
                responses = self._analyze_source_file(file_path)
                all_responses.extend(responses)
                progress.advance(task)

        return all_responses

    def _collect_files(self, repo_path: Path, patterns: List[str]) -> List[Path]:
        """Collect files matching glob patterns."""
        files = []
        for pattern in patterns:
            files.extend(repo_path.glob(pattern))
        return files

    def _analyze_build_file(self, file_path: Path) -> StructuredResponse:
        """Analyze single build file."""
        try:
            content = file_path.read_text()
            return self.build_upgrader.analyze(content, str(file_path))
        except Exception as e:
            self.console.print(
                f"❌ Error analyzing {file_path}: {e}", style="red")
            return None

    def _analyze_ci_file(self, file_path: Path) -> StructuredResponse:
        """Analyze single CI file."""
        try:
            content = file_path.read_text()
            return self.ci_upgrader.analyze(content, str(file_path))
        except Exception as e:
            self.console.print(
                f"❌ Error analyzing {file_path}: {e}", style="red")
            return None

    def _analyze_source_file(self, file_path: Path) -> List[StructuredResponse]:
        """Analyze source file, extracting modernizable code blocks."""
        try:
            content = file_path.read_text()

            keywords, upgrader = self._get_language_tools(file_path)
            if not upgrader:
                return []

            blocks = self.code_extractor.extract_blocks(
                str(file_path), content, keywords
            )

            if not blocks:
                return []

            responses = []
            for block in blocks:
                response = upgrader.analyze(block.content, str(file_path))
                if response and response.changes:
                    for change in response.changes:
                        change.location.start_line += block.start_line - 1
                        change.location.end_line += block.start_line - 1
                    responses.append(response)

            return responses

        except Exception as e:
            self.console.print(
                f"❌ Error analyzing {file_path}: {e}", style="red")
            return []

    def _get_language_tools(self, file_path: Path):
        """Get modernization keywords and upgrader for file type."""

        suffix_map = {
            ".java": (UpgraderConfig.UPGRADE_KEYWORDS_JAVA, self.java_upgrader),
            ".groovy": (UpgraderConfig.UPGRADE_KEYWORDS_GROOVY, self.groovy_upgrader),
            ".kt": (UpgraderConfig.UPGRADE_KEYWORDS_KOTLIN, self.kotlin_upgrader)
        }

        return suffix_map.get(file_path.suffix, ([], None))
