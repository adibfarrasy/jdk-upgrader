from src.upgraders.base_upgrader import BaseUpgrader


class KotlinUpgrader(BaseUpgrader):
    """Suggests Kotlin code upgrade opportunities for target JDK compatibility."""

    ANALYSIS_INSTRUCTIONS = """
    Check for:
    - Kotlin compiler version (1.7+ for JDK17, 2+ for JDK21)
    - Java interop issues with sealed classes/records
    - Reflection library compatibility
    - Coroutines with virtual threads conflicts
    - kotlinx library version requirements

    Focus on Kotlin/JVM compatibility while preserving application behavior.
    """

    PROMPT = """
    Analyze this Kotlin code for JDK {target_jdk} upgrade and suggest changes:
    ```kotlin
    {file_content}
    ```
    {analysis_instructions}
    {logic_preservation_prompt}
    {change_prompt}
    {extra_prompt}
    {format_instructions}
    """
