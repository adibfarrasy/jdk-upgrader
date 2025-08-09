from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse, Change, Location


class JavaModernizer:
    """Suggests Java code modernization opportunities for target JDK features."""

    PROMPT = """
    Analyze this Java code for JDK {target_jdk} modernization opportunities:
    ```java
    {code}
    ```
    
    Check for:
    - Deprecated/removed APIs (sun.*, java.security.Policy methods)
    - Reflection access issues (setAccessible warnings)
    - Module system conflicts (unnamed module accessing restricted packages)
    - Third-party dependencies requiring updates
    - Opportunities: records, text blocks, pattern matching, switch expressions
    
    {extra_prompt}

    Suggest modern Java version {target_jdk} alternatives.

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
        Analyze Java code and suggest target JDK modernizations.

        TODO:
        1. Parse Java source code to identify modernization opportunities
        2. Detect string concatenation patterns suitable for text blocks
        3. Find instanceof + cast patterns for pattern matching
        4. Identify verbose switch statements for switch expressions
        5. Look for opportunities to use records instead of POJOs
        6. Find stream operations that could use newer methods
        7. Suggest sealed classes where appropriate
        8. Check for try-with-resources improvements
        9. Identify null checks that could use Optional
        10. Ensure suggested changes maintain code semantics

        Args:
            code: Java source code content

        Returns:
            Modernization suggestions with before/after examples
        """
        return self.chain.run(code=code)
