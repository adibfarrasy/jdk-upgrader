from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse


class CIAnalyzer:
    """Analyzes CI/CD configuration files for JDK version updates."""

    ANALYSIS_INSTRUCTIONS = """
    Look for:
    - GitHub Actions/ Gitlab CI setup-java versions
    - Docker base image versions
    - Java version parameters
    - Build matrix configurations
    """

    PROMPT = """
    Analyze this CI configuration file for JDK {target_jdk} upgrade 
    and suggest changes:
    {file_content}
    
    {analysis_instructions}
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
        base_parser = PydanticOutputParser(pydantic_object=StructuredResponse)
        self.parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)
        self.prompt = PromptTemplate(
            template=self.PROMPT,
            input_variables=["file_content", "target_jdk"],
            partial_variables={
                "analysis_instructions": self.ANALYSIS_INSTRUCTIONS,
                "change_prompt": Config.CHANGE_PROMPT,
                "extra_prompt": Config.EXTRA_PROMPTS["analyzers"],
                "format_instructions": self.parser.get_format_instructions(),
            }
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, content: str, file_path: str) -> StructuredResponse:
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
