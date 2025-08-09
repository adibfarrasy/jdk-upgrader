from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse, Change, Location


class CIAnalyzer:
    """Analyzes CI/CD configuration files for JDK version updates."""

    PROMPT = """
    Analyze this CI configuration file for JDK {target_jdk} upgrade:
    {file_content}
    
    Look for:
    - GitHub Actions setup-java versions
    - Docker base image versions
    - Java version parameters
    - Build matrix configurations
    
    {extra_prompt}

    Return updated configuration with JDK {target_jdk}.

    {format_instructions}
    """

    def __init__(self, llm):
        """
        Initialize with LangChain LLM instance.

        Args:
            llm: Azure OpenAI LLM instance from config
        """
        self.parser = PydanticOutputParser(pydantic_object=StructuredResponse)
        self.prompt = PromptTemplate(
            template=self.PROMPT,
            input_variables=["file_content", "target_jdk", "extra_prompt"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, content: str, file_path: str) -> StructuredResponse:
        """
        Analyze CI configuration and return target JDK updates.

        TODO:
        1. Detect CI platform (GitHub Actions, GitLab CI, etc.)
        2. Find Java version specifications in the config
        3. Update setup-java action versions to latest
        4. Update java-version parameters to target JDK
        5. Update Docker base images (e.g. openjdk:21, etc.)
        6. Handle build matrices with multiple Java versions
        7. Preserve other configuration while updating Java parts

        Args:
            content: Raw content of CI configuration file

        Returns:
            Updated CI configuration with target JDK
        """
        try:
            result = self.chain.invoke(
                {
                    "file_content": content,
                    "target_jdk": Config.TARGET_JDK_VERSION,
                    "extra_prompt": Config.EXTRA_PROMPTS["analyzers"],
                }
            )

            for change in result.changes:
                change.location.file_path = file_path

            return result

        except Exception as e:
            # TODO: Handle parsing errors gracefully
            print(f"Failed to parse structured output: {e}")
            return StructuredResponse(
                summary=f"Failed to analyze CI config in {file_path} due to parsing error: {str(e)}",
                changes=[]
            )
