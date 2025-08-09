from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse
from src.modernizers import get_logic_preservation_prompt


class GroovyModernizer:
    """Suggests Groovy code modernization opportunities for target JDK compatibility."""

    ANALYSIS_INSTRUCTIONS = """
    Check for:
    - Groovy version compatibility (requires 3.0.9+ for JDK17+, 4.x for JDK21)
    - ASM/bytecode generation issues
    - Dynamic method dispatch changes
    - @CompileStatic annotations with new JDK features
    - Grape/dependency resolution problems
    """

    PROMPT = """
    Analyze this Groovy code for JDK {target_jdk} upgrade and suggest changes:
    ```groovy
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
            input_variables=["code", "target_jdk"],
            partial_variables={
                "analysis_instructions": self.ANALYSIS_INSTRUCTIONS,
                "change_prompt": Config.CHANGE_PROMPT,
                "extra_prompt": Config.EXTRA_PROMPTS["modernizers"],
                "format_instructions": self.parser.get_format_instructions(),
                "logic_preservation_prompt": get_logic_preservation_prompt("groovy"),
            }
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, code: str) -> str:
        return self.chain.run(code=code)
