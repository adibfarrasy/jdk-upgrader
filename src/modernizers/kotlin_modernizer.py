from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse
from src.modernizers import get_logic_preservation_prompt


class KotlinModernizer:
    """Suggests Kotlin code modernization opportunities for target JDK compatibility."""

    ANALYSIS_INSTRUCTIONS = """
    Check for:
    - Kotlin compiler version (1.7+ for JDK17, 2+ for JDK21)
    - Java interop issues with sealed classes/records
    - Reflection library compatibility
    - Coroutines with virtual threads conflicts
    - kotlinx library version requirements

    Focus on Kotlin/JVM compatibility while preserving application behavior.
    """

    PROMPT = """
    Analyze this Kotlin code for JDK {target_jdk} upgrade and suggest changes:
    ```kotlin
    {code}
    ```
    {analysis_instructions}
    {logic_preservation_prompt}
    {change_prompt}
    {extra_prompt}
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
                "analysis_instructions": self.ANALYSIS_INSTRUCTIONS,
                "change_prompt": Config.CHANGE_PROMPT,
                "extra_prompt": Config.EXTRA_PROMPTS["modernizers"],
                "format_instructions": self.parser.get_format_instructions(),
                "logic_preservation_prompt": get_logic_preservation_prompt("kotlin"),
            }
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, code: str) -> str:
        return self.chain.run(code=code)
