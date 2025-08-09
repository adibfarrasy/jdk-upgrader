from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate
from rich.console import Console

from config import Config
from src.models.response import StructuredResponse
from src.upgraders.prompts import get_logic_preservation_prompt


class BaseUpgrader:
    """Base class for all JDK upgraders."""

    # Subclasses should override these
    ANALYSIS_INSTRUCTIONS = ""
    PROMPT = ""

    def __init__(self, llm, console=None):
        """Initialize with LangChain LLM instance."""
        base_parser = PydanticOutputParser(pydantic_object=StructuredResponse)
        self.parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)
        self.prompt = PromptTemplate(
            template=self.PROMPT,
            input_variables=["file_content", "target_jdk"],
            partial_variables=self._get_partial_variables()
        )
        self.console = console or Console()
        self.chain = self.prompt | llm | self.parser

    def _get_partial_variables(self):
        """Get partial variables for prompt template."""

        # Get language from class name (JavaUpgrader -> java)
        language = self.__class__.__name__.replace("Upgrader", "").lower()

        return {
            "analysis_instructions": self.ANALYSIS_INSTRUCTIONS,
            "change_prompt": Config.CHANGE_PROMPT,
            "extra_prompt": Config.EXTRA_PROMPTS.get("upgraders", ""),
            "format_instructions": self.parser.get_format_instructions(),
            "logic_preservation_prompt": get_logic_preservation_prompt(language),
        }

    def analyze(self, file_content: str, file_path: str) -> StructuredResponse:
        """Analyze code for JDK upgrade opportunities."""
        try:
            result = self.chain.invoke({
                "file_content": file_content,
                "target_jdk": Config.TARGET_JDK_VERSION
            })

            for change in result.changes:
                change.location.file_path = file_path

            return result

        except Exception as e:
            self.console.print(f"Failed to analyze code: {e}", style="red")
            return StructuredResponse(
                summary=f"Failed to analyze due to parsing error: {str(e)}",
                changes=[]
            )
