from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse


class BuildFileAnalyzer:
    """Analyzes build files (Gradle/Maven) for target JDK compatibility and modernization."""

    ANALYSIS_INSTRUCTIONS = """
    Examine ALL of the following areas:
    
    1. JAVA VERSION SETTINGS:
       - sourceCompatibility and targetCompatibility
       - Java toolchain configurations
       - Compiler options and release targets
    
    2. PLUGIN VERSIONS:
       - Core plugins (java, groovy, kotlin)
       - Framework plugins (Spring Boot, etc.)
       - Build tool plugins that need JDK {target_jdk} support
    
    3. DEPENDENCY VERSIONS:
       - Library versions in dependencies block
       - Check JDK {target_jdk} compatibility for each dependency
       - Suggest minimum versions that support JDK {target_jdk}
       - Flag any incompatible dependencies
    
    4. BUILD CONFIGURATIONS:
       - Gradle/Maven version compatibility
       - Compiler arguments and JVM options
       - Test configurations for JDK {target_jdk}
    
    5. SYNTAX MODERNIZATION:
       - Gradle DSL improvements
       - Dependency declaration syntax updates
       - Plugin configuration modernization
    """

    PROMPT = """
    Analyze this build file for JDK {target_jdk} upgrade and suggest changes:
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
            llm: LangChain LLM instance (AzureChatOpenAI)
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
            },
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, content: str, file_path: str) -> StructuredResponse:
        try:
            result = self.chain.invoke(
                {
                    "file_content": content,
                    "target_jdk": Config.TARGET_JDK_VERSION,
                }
            )

            for change in result.changes:
                change.location.file_path = file_path

            return result

        except Exception as e:
            # TODO: Handle parsing errors gracefully
            print(f"Failed to parse structured output: {e}")
            return StructuredResponse(
                summary=f"Failed to analyze build file {file_path} due to parsing error: {str(e)}",
                changes=[]
            )
