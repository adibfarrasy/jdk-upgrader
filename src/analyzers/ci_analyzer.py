from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class CIAnalyzer:
    """Analyzes CI/CD configuration files for JDK version updates."""

    PROMPT = """
    Analyze this CI configuration file for JDK 21 upgrade:
    {file_content}
    
    Look for:
    - GitHub Actions setup-java versions
    - Docker base image versions
    - Java version parameters
    - Build matrix configurations
    
    Return updated configuration with JDK 21.
    """

    def __init__(self, llm):
        """
        Initialize with LangChain LLM instance.

        Args:
            llm: Azure OpenAI LLM instance from config
        """
        self.chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=["file_content"], template=self.PROMPT
            ),
        )

    def analyze(self, content: str) -> str:
        """
        Analyze CI configuration and return JDK 21 updates.

        TODO:
        1. Detect CI platform (GitHub Actions, GitLab CI, etc.)
        2. Find Java version specifications in the config
        3. Update setup-java action versions to latest
        4. Update java-version parameters to '21'
        5. Update Docker base images (openjdk:21, etc.)
        6. Handle build matrices with multiple Java versions
        7. Preserve other configuration while updating Java parts

        Args:
            content: Raw content of CI configuration file

        Returns:
            Updated CI configuration with JDK 21
        """
        return self.chain.run(file_content=content)
