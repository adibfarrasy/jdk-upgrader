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
```bash
# Run modernization on your project
python main.py --project-path /path/to/gradle/project

# With specific file patterns
python main.py --project-path ./my-app --include "*.java,*.groovy"

# Dry run (analyze and show diffs, but don't write files)
python main.py --project-path ./my-app --dry-run
```
