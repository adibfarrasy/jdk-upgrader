from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class GradleAnalyzer:
    """Analyzes Gradle build files for JDK version updates."""

    PROMPT = """
    Analyze this build.gradle file for JDK 21 upgrade opportunities:
    {file_content}
    
    Look for:
    - sourceCompatibility and targetCompatibility settings
    - Java version declarations
    - Outdated plugin versions that need JDK 21 compatibility
    - Dependencies that may need version updates
    
    Return specific line-by-line changes needed.
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
        Analyze Gradle file content and return upgrade suggestions.

        TODO:
        1. Parse the file content to identify current Java version settings
        2. Use LLM to suggest specific line changes for JDK 21
        3. Format response as exact replacement text
        4. Handle both Groovy and Kotlin DSL syntax
        5. Validate that suggested changes are syntactically correct

        Args:
            content: Raw content of build.gradle file

        Returns:
            Suggested file content with JDK 21 updates
        """
        return self.chain.run(file_content=content)
