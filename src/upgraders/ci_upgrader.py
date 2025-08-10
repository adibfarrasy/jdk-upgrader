from src.upgraders.base_upgrader import BaseUpgrader


class CIUpgrader(BaseUpgrader):
    """Analyzes CI/CD configuration files for JDK version updates."""

    ANALYSIS_INSTRUCTIONS = """
    Look for:
    - GitHub Actions/ Gitlab CI setup-java versions
    - Docker base image versions
    - Java version parameters
    - Build matrix configurations
    """

    PROMPT = """
    Analyze this CI configuration file for JDK {target_jdk} upgrade
    and suggest changes:
    {file_content}

    When specifying line numbers in your changes, count from line 1
    at the top of the file.
    
    {analysis_instructions}
    {change_prompt}
    {extra_prompt}
    {format_instructions}
    """
