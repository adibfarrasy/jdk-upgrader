from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class KotlinModernizer:
    """Suggests Kotlin code modernization opportunities for JDK 21 compatibility."""

    PROMPT = """
    Analyze this Kotlin code for JDK 21 modernization:
    {code}
    
    Look for:
    - Kotlin DSL build script improvements for Gradle
    - JVM target updates to JDK 21
    - Kotlin/JVM interop improvements with JDK 21
    - Coroutines optimizations for JDK 21
    - Kotlin compiler options for JDK 21
    
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
        Analyze Kotlin code and suggest JDK 21 improvements.

        TODO:
        1. Parse Kotlin syntax (both .kt source and .kts build files)
        2. Identify Gradle Kotlin DSL patterns to modernize
        3. Check kotlinOptions jvmTarget settings for JDK 21
        4. Look for Kotlin compiler arguments that benefit from JDK 21
        5. Find coroutines patterns that can leverage JDK 21 features
        6. Suggest better type inference with newer Kotlin versions
        7. Identify extension functions that could use JDK 21 APIs
        8. Check for deprecated Kotlin/JVM interop patterns
        9. Look for build configuration improvements (compileKotlin, etc.)
        10. Handle both Kotlin source files and Kotlin DSL build scripts
        11. Suggest Kotlin version updates compatible with JDK 21
        12. Identify opportunities to use value classes with JDK 21

        Args:
            code: Kotlin source code or Kotlin DSL build script content

        Returns:
            Modernization suggestions for Kotlin + JDK 21
        """
        return self.chain.run(code=code)
