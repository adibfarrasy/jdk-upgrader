# target JDK Modernization Tool

An AI-powered tool that automatically analyzes and modernizes Java, Groovy, and Kotlin projects for target JDK compatibility. The tool uses LLM analysis to suggest code improvements, build configuration updates, and automatically fixes compilation errors with human oversight.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI API access
- Gradle project with Java/Groovy/Kotlin code
- `gradlew` or `gradle` available in project root

### Installation
```bash
# Clone and install dependencies
git clone <repository>
cd <repository>
pip install -r requirements.txt

# Install required packages
pip install langchain openai rich pathlib
```

### Basic Usage
> NOTE: Update `config.py` with your token first before proceeding

```bash
# Run modernization on your project
python main.py --project-path /path/to/gradle/project

# With specific file patterns
python main.py --project-path ./my-app --include "*.java,*.groovy"

# Dry run (analyze and show diffs, but don't write files)
python main.py --project-path ./my-app --dry-run
```

## 📁 Project Structure

```
src/
├── analyzers/                 # File analysis for modernization opportunities
│   ├── ci_analyzer.py         #   → CI/CD config analyzer
│   ├── dependency_analyzer.py #   → Gradle dependencies compatibility
│   └── gradle_analyzer.py     #   → build.gradle modernization
│
├── build_fixers/              # Post-modernization compilation fixes
│   └── build_error_handler.py #   → Gradle build runner and error fixing
│
├── config/                     # Configuration and constants
│   └── modernization_config.py #   → Global settings and patterns
│
├── generators/            # Patch generation and application
│   └── patch_generator.py #   → Creates and applies file patches
│
├── modernizers/             # Language-specific modernization
│   ├── groovy_modernizer.py #   → Groovy + Gradle build scripts
│   ├── java_modernizer.py   #   → Java code patterns for target JDK
│   └── kotlin_modernizer.py #   → Kotlin DSL and source files
│
├── utils/             # Language-specific modernization
│   └── code_extractor.py #   → Smart code block extraction
│
└── reviewer.py           #   → Human-in-the-loop review interface
```
