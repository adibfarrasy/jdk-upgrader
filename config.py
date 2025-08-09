import os
from typing import Optional


class Config:
    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_ENDPOINT: str = os.getenv(
        "AZURE_ENDPOINT", "https://achat.advai.net/api/v1/openai/proxy"
    )
    AZURE_API_VERSION: str = "2025-04-01-preview"
    AZURE_DEPLOYMENT_NAME: str = os.getenv(
        "AZURE_DEPLOYMENT_NAME", "gpt4o-mini")

    TEMPERATURE: float = 0.1

    # NOTE:
    # It is a deliberate decision NOT to update user-defined Gradle scripts
    BUILD_FILES = [
        # Gradle
        "**/build.gradle",
        "**/build.gradle.kts",
        "**/settings.gradle",
        "**/settings.gradle.kts",

        # Maven
        "**/pom.xml",
    ]
    CI_FILES = ["Dockerfile", ".gitlab-ci.yml", ".gitlab-ci.yaml"]
    SOURCE_FILES = ["**/*.java", "**/*.groovy", "**/*.kt"]

    CHANGE_PROMPT = """
        For each change needed, specify the change type and provide appropriate details:

        **INSERT changes** (adding new code):
        1. Identify the exact line number where new code should be inserted
        2. Provide the new code to insert (leave 'before' empty)
        3. Explain why this addition is necessary for JDK {target_jdk}
        4. Consider placement relative to existing code (imports, dependencies, etc.)

        **UPDATE changes** (modifying existing code):
        1. Identify the exact lines that need modification (start_line to end_line)
        2. Provide both the current code (before) and replacement code (after)
        3. Explain why the change is necessary for JDK {target_jdk}
        4. Ensure the replacement maintains the same functionality with modern syntax

        **DELETE changes** (removing obsolete code):
        1. Identify the exact lines that need removal (start_line to end_line)
        2. Provide the current code to be deleted (leave 'after' empty)
        3. Explain why this code is obsolete or incompatible with JDK {target_jdk}
        4. Ensure removal doesn't break dependencies or required functionality

        **General considerations for all changes:**
        - Consider dependencies between changes (e.g., plugin updates before dependency updates)
        - Maintain proper ordering (imports before usage, declarations before references)
        - Preserve code formatting and indentation style
        - Ensure changes work together as a cohesive set
        - Validate that line numbers are accurate and non-overlapping
    """

    EXTRA_PROMPTS = {
        "analyzers": os.getenv("EXTRA_PROMPT_ANALYZERS", ""),
        "build_fixers": os.getenv("EXTRA_PROMPT_BUILD_FIXERS", ""),
        "modernizers": os.getenv("EXTRA_PROMPT_MODERNIZERS", ""),
    }

    TARGET_JDK_VERSION = "21"

    @classmethod
    def validate(cls):
        if not cls.AZURE_OPENAI_API_KEY:
            raise ValueError(
                "AZURE_OPENAI_API_KEY environment variable required")
