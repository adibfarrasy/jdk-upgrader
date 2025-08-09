from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse, Change, Location


class GroovyModernizer:
    """Suggests Groovy code modernization opportunities for target JDK compatibility."""

    PROMPT = """
    Analyze this Groovy code for JDK {target_jdk} modernization:
    ```groovy
    {code}
    ```
    
    Check for:
    - Groovy version compatibility (requires 3.0.9+ for JDK17+, 4.x for JDK21)
    - ASM/bytecode generation issues
    - Dynamic method dispatch changes
    - @CompileStatic annotations with new JDK features
    - Grape/dependency resolution problems
    
    {extra_prompt}

    Suggest improvements for JDK {target_jdk} compatibility.

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
            input_variables=["code", "target_jdk", "extra_prompt"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, code: str) -> str:
        """
        Analyze Groovy code and suggest target JDK improvements.

        TODO:
        1. Parse Groovy syntax (both script and class files)
        2. Identify Gradle build script patterns to modernize
        3. Check dependency declarations for newer syntax
        4. Look for plugin configurations that can be improved
        5. Find Groovy-specific patterns that benefit from target JDK
        6. Suggest better type annotations where helpful
        7. Identify closure patterns that could be simplified
        8. Check for deprecated Groovy methods/syntax
        9. Ensure compatibility with latest Gradle + target JDK
        10. Handle both Groovy source files and build scripts

        Args:
            code: Groovy source code or build script content

        Returns:
            Modernization suggestions for Groovy + target JDK
        """
        return self.chain.run(code=code)
