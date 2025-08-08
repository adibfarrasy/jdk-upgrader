from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class DependencyAnalyzer:
    """Analyzes project dependencies for JDK 21 compatibility."""

    PROMPT = """
    Analyze these dependencies for JDK 21 compatibility:
    {dependencies}
    
    For each dependency:
    - Check if current version supports JDK 21
    - Suggest minimum version that supports JDK 21
    - Flag any that are incompatible
    
    Return dependency updates needed.
    """

    def __init__(self, llm):
        """
        Initialize with LangChain LLM instance.

        Args:
            llm: Azure OpenAI LLM instance from config
        """
        self.chain = LLMChain(
            llm=llm,
            prompt=PromptTemplate(
                input_variables=["dependencies"], template=self.PROMPT
            ),
        )

    def analyze(self, dependencies: list) -> str:
        """
        Analyze dependencies for JDK 21 compatibility.

        TODO:
        1. Parse dependency declarations from build files
        2. Extract library names and current versions
        3. Check each dependency against JDK 21 compatibility matrix
        4. Suggest version updates for incompatible dependencies
        5. Flag dependencies that have no JDK 21 support
        6. Handle both Maven and Gradle dependency formats
        7. Consider transitive dependency impacts
        8. Prioritize critical vs optional dependency updates

        Args:
            dependencies: List of dependency strings from build file

        Returns:
            Dependency update recommendations
        """
        deps_text = "\n".join(dependencies)
        return self.chain.run(dependencies=deps_text)
