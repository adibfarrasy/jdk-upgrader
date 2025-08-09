from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse, Change, Location


class BuildFileAnalyzer:
    """Analyzes build files (Gradle/Maven) for target JDK compatibility and modernization."""

    PROMPT = """
    Analyze this build file for JDK {target_jdk} upgrade and modernization:
    {file_content}
    
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
    
    For each change needed:
    1. Identify the exact lines that need modification
    2. Provide the current code and the replacement code
    3. Explain why the change is necessary for JDK {target_jdk}
    4. Consider dependencies between changes (e.g., plugin updates before dependency updates)
    
    {extra_prompt}

    Return comprehensive analysis in the specified JSON format.

    {format_instructions}
    """

    def __init__(self, llm):
        """
        Initialize with LangChain LLM instance.

        Args:
            llm: LangChain LLM instance (AzureChatOpenAI)
        """
        self.parser = PydanticOutputParser(pydantic_object=StructuredResponse)
        self.prompt = PromptTemplate(
            template=self.PROMPT,
            input_variables=["file_content", "target_jdk", "extra_prompt"],
            partial_variables={
                "format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, content: str, file_path: str) -> StructuredResponse:
        """
        Analyze build file for comprehensive target JDK modernization.

        TODO:
        1. Detect build system type (Gradle vs Maven, Groovy vs Kotlin DSL)
        2. Parse current Java version settings and plugin versions
        3. Extract dependency declarations and versions
        4. Check target JDK compatibility for all components
        5. Suggest coordinated updates (plugins before dependencies)
        6. Handle both build configuration and dependency management
        7. Consider build script syntax modernization opportunities
        8. Validate suggested changes work together
        9. Prioritize changes by impact and risk

        Args:
            content: Raw content of build file (build.gradle, pom.xml, etc.)
            file_path: Path to the build file (for location references)

        Returns:
            StructuredResponse with comprehensive modernization changes
        """
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
                summary=f"Failed to analyze build file {file_path} due to parsing error: {str(e)}",
                changes=[]
            )
