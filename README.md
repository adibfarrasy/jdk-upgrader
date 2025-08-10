# JDK Upgrade Tool

An AI-powered tool that automatically analyzes and modernizes Java, Groovy, and Kotlin projects for target JDK compatibility. The tool uses LLM analysis to suggest code improvements, build configuration updates, and automatically fixes compilation errors with human oversight.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Azure OpenAI API access
- Project with Java/Groovy/Kotlin source code and Gradle/ Maven scripts

### Installation
```bash
# Clone and install dependencies
git clone <repository>
cd <repository>
pip install -r requirements.txt
```

### Basic Usage
```bash
# Install just
# https://github.com/casey/just

# Run JDK upgrade on your project
just run /path/to/project
# or `python main.py --project-path /path/to/project`

# With auto-approve changes
just auto /path/to/project
# or `python main.py --project-path /path/to/project --auto-approve`

# Dry run (analyze and show diffs, but don't write files)
just dry-run /path/to/project 
# or `python main.py --project-path ./my-app --dry-run`
```
