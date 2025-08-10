from src.upgraders.base_upgrader import BaseUpgrader


class BuildUpgrader(BaseUpgrader):
    """Analyzes build files (Gradle/Maven) for target JDK compatibility and upgrade."""

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
