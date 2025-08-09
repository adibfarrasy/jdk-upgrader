from src.upgraders.base_upgrader import BaseUpgrader


class JavaUpgrader(BaseUpgrader):
    """Suggests Java code upgrade opportunities for target JDK features."""

    ANALYSIS_INSTRUCTIONS = """
    Check for:
    - Deprecated/removed APIs (sun.*, java.security.Policy methods)
    - Reflection access issues (setAccessible warnings)
    - Module system conflicts (unnamed module accessing restricted packages)
    - Third-party dependencies requiring updates
    - Opportunities: records, text blocks, pattern matching, switch expressions
    """

    PROMPT = """
    Analyze this Java code for JDK {target_jdk} upgrade and suggest changes:
    ```java
    {file_content}
    ```
    
    {analysis_instructions}
    {logic_preservation_prompt}
    {change_prompt}
    {extra_prompt}
    {format_instructions}
    """
