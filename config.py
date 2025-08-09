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
