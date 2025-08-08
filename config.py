import os
from typing import Optional


class Config:
    # Azure OpenAI settings
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv("AZURE_OPENAI_API_KEY")
    AZURE_ENDPOINT: str = os.getenv(
        "AZURE_ENDPOINT", "https://achat.advai.net/api/v1/openai/proxy"
    )
    AZURE_API_VERSION: str = "2025-04-01-preview"
    AZURE_DEPLOYMENT_NAME: str = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt4o-mini")

    TEMPERATURE: float = 0.1

    BUILD_FILES = ["build.gradle", "build.gradle.kts"]
    CI_FILES = ["Dockerfile", ".gitlab-ci.yaml"]
    TARGET_JDK_VERSION = "21"

    @classmethod
    def validate(cls):
        if not cls.AZURE_OPENAI_API_KEY:
            raise ValueError("AZURE_OPENAI_API_KEY environment variable required")
