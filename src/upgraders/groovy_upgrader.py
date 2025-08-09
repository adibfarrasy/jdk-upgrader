from src.upgraders.base_upgrader import BaseUpgrader


class GroovyUpgrader(BaseUpgrader):
    """Suggests Groovy code upgrade opportunities for target JDK compatibility."""

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
    {file_content}
    ```

    {analysis_instructions}
    {logic_preservation_prompt}
    {change_prompt}
    {extra_prompt}
    {format_instructions}
    """
