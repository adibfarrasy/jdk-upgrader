import subprocess
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from src.utils.code_extractor import CodeBlockExtractor


@dataclass
class BuildError:
    """Represents a compilation error from Gradle build."""

    file_path: str
    line_number: int
    column_number: Optional[int]
    error_type: str
    message: str
    severity: str  # ERROR, WARNING

    @property
    def is_actionable(self) -> bool:
        """Check if error is worth sending to LLM for fixing."""
        # TODO: Define which error types are actionable
        return self.severity == "ERROR"


class GradleBuildRunner:
    """Runs Gradle builds and captures errors."""

    def __init__(self, project_root: Path):
        """
        Initialize build runner.

        Args:
            project_root: Root directory of Gradle project
        """
        self.project_root = project_root

    def run_build(self) -> tuple[bool, List[BuildError]]:
        """
        Run gradle build and return success status with any errors.

        TODO:
        1. Execute 'gradle build' or './gradlew build' in project_root
        2. Capture both stdout and stderr
        3. Parse output for compilation errors using regex patterns
        4. Extract file paths, line numbers, error messages
        5. Handle different Gradle output formats
        6. Return structured BuildError objects
        7. Distinguish between compile errors vs test failures
        8. Set appropriate timeout for build process

        Returns:
            (success: bool, errors: List[BuildError])
        """
        # TODO: Implement actual Gradle execution
        try:
            result = subprocess.run(
                ["./gradlew", "compileJava", "compileGroovy"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            # TODO: Parse result.stdout and result.stderr for errors
            errors = self._parse_gradle_output(result.stdout + result.stderr)

            return result.returncode == 0, errors

        except subprocess.TimeoutExpired:
            # TODO: Handle build timeout
            return False, [BuildError(
                file_path="BUILD_TIMEOUT",
                line_number=0,
                column_number=None,
                error_type="TIMEOUT",
                message="Gradle build timed out after 5 minutes",
                severity="ERROR"
            )]
        except Exception as e:
            # TODO: Handle other build failures
            return False, [BuildError(
                file_path="BUILD_SYSTEM",
                line_number=0,
                column_number=None,
                error_type="SYSTEM_ERROR",
                message=f"Build system error: {e}",
                severity="ERROR"
            )]

    def _parse_gradle_output(self, output: str) -> List[BuildError]:
        """
        Parse Gradle build output to extract compilation errors.

        TODO:
        1. Use regex patterns to match Gradle error formats:
           - Java: "File.java:15: error: cannot find symbol"
           - Groovy: "File.groovy: 20: unexpected token"
        2. Extract file path, line number, column (if available)
        3. Classify error types (syntax, type, import, etc.)
        4. Filter out non-actionable errors (warnings, test failures)
        5. Handle multi-line error messages
        6. Parse both javac and groovy compiler output formats
        7. Handle relative vs absolute file paths

        Args:
            output: Combined stdout/stderr from Gradle

        Returns:
            List of parsed BuildError objects
        """
        errors = []

        # TODO: Implement regex parsing patterns
        # Example patterns:
        # Java: r"([^:]+\.java):(\d+): error: (.+)"
        # Groovy: r"([^:]+\.groovy): (\d+): (.+)"

        return errors


class CompilationErrorFixer:
    """Uses LLM to suggest fixes for compilation errors."""

    MAX_FIX_ATTEMPTS = 2

    def __init__(self, llm, code_extractor: CodeBlockExtractor):
        """
        Initialize error fixer.

        Args:
            llm: LangChain LLM instance
            code_extractor: Code block extractor for context
        """
        self.llm = llm
        self.code_extractor = code_extractor
        self.fix_attempts = {}  # Track attempts per file

    def suggest_fixes(self, errors: List[BuildError]) -> Dict[str, str]:
        """
        Analyze compilation errors and suggest fixes.

        TODO:
        1. Group errors by file to batch process
        2. For each file with errors:
           - Use CodeBlockExtractor to get context around error lines
           - Expand context slightly for imports/class declarations
           - Format error messages clearly for LLM
        3. Create LLM prompt with:
           - Error messages with line numbers
           - Relevant code context
           - Instructions to fix compilation issues only
        4. Parse LLM response for complete file content
        5. Validate suggested fixes are reasonable
        6. Return dict of {file_path: suggested_content}
        7. Track fix attempts to enforce MAX_FIX_ATTEMPTS limit

        Args:
            errors: List of compilation errors to fix

        Returns:
            Dict mapping file paths to suggested fixed content
        """
        fixes = {}

        # TODO: Group errors by file
        errors_by_file = self._group_errors_by_file(errors)

        for file_path, file_errors in errors_by_file.items():
            # TODO: Check attempt limit
            if self._get_attempt_count(file_path) >= self.MAX_FIX_ATTEMPTS:
                print(f"⚠️  Skipping {file_path} - max attempts reached")
                continue

            # TODO: Get code context for errors
            context = self._get_error_context(file_path, file_errors)

            if context:
                # TODO: Generate LLM prompt and get suggested fix
                suggested_fix = self._generate_fix(
                    file_path, file_errors, context)
                if suggested_fix:
                    fixes[file_path] = suggested_fix
                    self._increment_attempt_count(file_path)

        return fixes

    def _group_errors_by_file(self, errors: List[BuildError]) -> Dict[str, List[BuildError]]:
        """
        Group errors by file path for batch processing.

        TODO:
        1. Filter only actionable errors
        2. Group by file_path
        3. Sort errors within each file by line number
        4. Limit to reasonable number of errors per file

        Args:
            errors: List of all build errors

        Returns:
            Dict mapping file paths to their errors
        """
        # TODO: Implement grouping logic
        return {}

    def _get_error_context(self, file_path: str, errors: List[BuildError]) -> Optional[str]:
        """
        Extract code context around compilation errors.

        TODO:
        1. Read file content
        2. Use CodeBlockExtractor to get blocks around error lines
        3. Expand context to include:
           - Import statements at top of file
           - Class/method declarations containing errors
           - Related variable declarations
        4. Merge overlapping contexts
        5. Add line numbers for LLM reference
        6. Keep total context under reasonable token limit

        Args:
            file_path: Path to file with errors
            errors: List of errors in this file

        Returns:
            Code context string or None if unavailable
        """
        # TODO: Implement context extraction
        return None

    def _generate_fix(self, file_path: str, errors: List[BuildError], context: str) -> Optional[str]:
        """
        Generate LLM prompt and get suggested fix.

        TODO:
        1. Create clear prompt with:
           - File path and language detection
           - List of compilation errors with line numbers
           - Code context around errors
           - Instructions to fix ONLY compilation issues
           - Request complete corrected file content
        2. Call LLM with prompt
        3. Parse and validate response
        4. Check that response looks like valid code
        5. Return suggested file content

        Args:
            file_path: Path being fixed
            errors: Compilation errors in file
            context: Code context around errors

        Returns:
            Suggested complete file content or None
        """
        # TODO: Implement LLM fix generation
        return None

    def _get_attempt_count(self, file_path: str) -> int:
        """Get number of fix attempts for file."""
        return self.fix_attempts.get(file_path, 0)

    def _increment_attempt_count(self, file_path: str):
        """Increment fix attempt counter for file."""
        self.fix_attempts[file_path] = self._get_attempt_count(file_path) + 1

    def reset_attempts(self):
        """Reset attempt counters (for new modernization session)."""
        self.fix_attempts.clear()


class BuildErrorHandler:
    """Orchestrates the build-test-fix cycle."""

    def __init__(self, project_root: Path, llm, reviewer):
        """
        Initialize build error handler.

        Args:
            project_root: Gradle project root directory
            llm: LangChain LLM instance  
            reviewer: HumanReviewer instance
        """
        self.build_runner = GradleBuildRunner(project_root)
        self.error_fixer = CompilationErrorFixer(llm, CodeBlockExtractor())
        self.reviewer = reviewer

    def handle_post_modernization_build(self) -> bool:
        """
        Run build after modernization and fix any compilation errors.

        TODO:
        1. Run initial build to check for errors
        2. If build succeeds, return True
        3. If build fails:
           - Collect and analyze errors
           - Get LLM suggested fixes
           - Present fixes to human for review
           - Apply approved fixes
           - Retry build (up to MAX_FIX_ATTEMPTS)
        4. Report final status and any unfixable errors
        5. Handle edge cases (no errors found but build failed)

        Returns:
            True if build eventually succeeds, False otherwise
        """
        print("🔨 Running post-modernization build...")

        for attempt in range(1, CompilationErrorFixer.MAX_FIX_ATTEMPTS + 1):
            # TODO: Run build
            success, errors = self.build_runner.run_build()

            if success:
                print("✅ Build successful!")
                return True

            # TODO: Filter actionable errors
            actionable_errors = [e for e in errors if e.is_actionable]

            if not actionable_errors:
                print("❌ Build failed but no actionable errors found")
                return False

            print(
                f"❌ Build failed with {len(actionable_errors)} errors (attempt {attempt})")

            # TODO: Get suggested fixes
            suggested_fixes = self.error_fixer.suggest_fixes(actionable_errors)

            if not suggested_fixes:
                print("❌ No fixes could be generated")
                return False

            # TODO: Review fixes with human
            applied_any = False
            for file_path, suggested_content in suggested_fixes.items():
                if self.reviewer.review_and_apply(Path(file_path), suggested_content):
                    applied_any = True

            if not applied_any:
                print("❌ No fixes were applied")
                return False

            print(f"🔄 Applied fixes, retrying build...")

        print(
            f"❌ Build still failing after {CompilationErrorFixer.MAX_FIX_ATTEMPTS} attempts")
        return False
