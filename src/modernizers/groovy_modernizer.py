from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class GroovyModernizer:
    """Suggests Groovy code modernization opportunities for JDK 21 compatibility."""

    PROMPT = """
    Analyze this Groovy code for JDK 21 modernization:
    {code}
    
    Look for:
    - Groovy features that work better with JDK 21
    - Build script improvements for Gradle
    - Dependency syntax modernization
    - Plugin configuration updates
    
    Suggest improvements for JDK 21 compatibility.
    """

    def __init__(self, llm):
        """
        Initialize with LangChain LLM instance.

        Args:
            llm: Azure OpenAI LLM instance from config
        """
        self.chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(input_variables=["code"], template=self.PROMPT),
        )

    def analyze(self, code: str) -> str:
        """
        Analyze Groovy code and suggest JDK 21 improvements.

        TODO:
        1. Parse Groovy syntax (both script and class files)
        2. Identify Gradle build script patterns to modernize
        3. Check dependency declarations for newer syntax
        4. Look for plugin configurations that can be improved
        5. Find Groovy-specific patterns that benefit from JDK 21
        6. Suggest better type annotations where helpful
        7. Identify closure patterns that could be simplified
        8. Check for deprecated Groovy methods/syntax
        9. Ensure compatibility with latest Gradle + JDK 21
        10. Handle both Groovy source files and build scripts

        Args:
            code: Groovy source code or build script content

        Returns:
            Modernization suggestions for Groovy + JDK 21
        """
        return self.chain.run(code=code)
