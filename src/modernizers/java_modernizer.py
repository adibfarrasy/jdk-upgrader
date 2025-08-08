from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate


class JavaModernizer:
    """Suggests Java code modernization opportunities for JDK 21 features."""

    PROMPT = """
    Analyze this Java code for JDK 21 modernization opportunities:
    {code}
    
    Look for:
    - String concatenation that could use text blocks
    - instanceof checks that could use pattern matching
    - Verbose switch statements that could use switch expressions
    - Stream operations that could be simplified
    - Record class opportunities
    
    Suggest modern Java 21 alternatives.
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
        Analyze Java code and suggest JDK 21 modernizations.

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
