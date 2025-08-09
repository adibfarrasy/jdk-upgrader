from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate

from config import Config
from src.models.response import StructuredResponse, Change, Location


class KotlinModernizer:
    """Suggests Kotlin code modernization opportunities for target JDK compatibility."""

    PROMPT = """
    Analyze this Kotlin code for JDK {target_jdk} modernization:
    ```kotlin
    {code}
    ```
    
    Check for:
    - Kotlin compiler version (1.7+ for JDK17, 2+ for JDK21)
    - Java interop issues with sealed classes/records
    - Reflection library compatibility
    - Coroutines with virtual threads conflicts
    - kotlinx library version requirements
    
    Suggest improvements for JDK {target_jdk} compatibility.
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
                "format_instructions": self.parser.get_format_instructions()}
        )
        self.chain = self.prompt | llm | self.parser

    def analyze(self, code: str) -> str:
        """
        Analyze Kotlin code and suggest target JDK improvements.

        TODO:
        1. Parse Kotlin syntax (both .kt source and .kts build files)
        2. Identify Gradle Kotlin DSL patterns to modernize
        3. Check kotlinOptions jvmTarget settings for target JDK
        4. Look for Kotlin compiler arguments that benefit from target JDK
        5. Find coroutines patterns that can leverage target JDK features
        6. Suggest better type inference with newer Kotlin versions
        7. Identify extension functions that could use target JDK APIs
        8. Check for deprecated Kotlin/JVM interop patterns
        9. Look for build configuration improvements (compileKotlin, etc.)
        10. Handle both Kotlin source files and Kotlin DSL build scripts
        11. Suggest Kotlin version updates compatible with target JDK
        12. Identify opportunities to use value classes with target JDK

        Args:
            code: Kotlin source code or Kotlin DSL build script content

        Returns:
            Modernization suggestions for Kotlin + target JDK
        """
        return self.chain.run(code=code)
