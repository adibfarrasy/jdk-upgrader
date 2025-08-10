import os

LOGIC_PRESERVATION_PROMPT = """
**CRITICAL: PRESERVE BUSINESS LOGIC**

When modernizing code, you MUST maintain identical behavior and business logic.
Follow these strict rules:

**1. SYNTAX-ONLY CHANGES:**
- Update only language syntax and APIs, never logic flow
- Modernize HOW code is written, not WHAT it does
- If unsure whether a change affects logic, do NOT make the change
- Prefer explicitly written type over type inference like `var`

**2. BEHAVIORAL EQUIVALENCE:**
- Ensure output is identical for all possible inputs
- Preserve error handling and exception behavior
- Maintain performance characteristics where possible
- Keep side effects exactly the same

**3. FORBIDDEN CHANGES:**
❌ Changing conditional logic or control flow
❌ Modifying method signatures or return types
❌ Altering exception handling behavior
❌ Changing null handling semantics
❌ Modifying concurrent behavior or thread safety
❌ Changing validation rules or business constraints

**4. VALIDATION REQUIREMENTS:**
- Before suggesting any change, verify it's purely syntactic
- For complex transformations, provide detailed justification
- If behavior might change even slightly, mark as "REVIEW REQUIRED"
- When in doubt, suggest the change as a comment for manual review

**Remember: Modernization should be invisible to the end user - only developers see the improved code quality.**
"""

# Language-specific safe modernization examples
JAVA_SAFE_EXAMPLES = """
**SAFE JAVA UPGRADES:**
✅ `Arrays.asList(a, b, c)` → `List.of(a, b, c)`
✅ `if (x instanceof String) { String s = (String) x; }` → `if (x instanceof String s) {`
✅ String concatenation → Text blocks (preserving exact formatting)
✅ `switch` statements → `switch` expressions (same case logic)
✅ `new ArrayList<>()` → `List.of()` (only for immutable collections)
"""

GROOVY_SAFE_EXAMPLES = """
**SAFE GROOVY UPGRADES:**
✅ `compile 'group:artifact:version'` → `implementation 'group:artifact:version'`
✅ `apply plugin: 'java'` → `plugins { id 'java' }`
✅ Old closure syntax → Modern DSL (preserving same configuration)
✅ `configurations.compile` → `configurations.implementation`
✅ Gradle 3.x syntax → Gradle 7.x syntax (same build behavior)
"""

KOTLIN_SAFE_EXAMPLES = """
**SAFE KOTLIN UPGRADES:**
✅ `jvmTarget = "1.8"` → `jvmTarget = "21"`
✅ `kotlin("jvm") version "1.5.0"` → `kotlin("jvm") version "1.9.0"`
✅ Old coroutines APIs → Modern stable APIs (same concurrency behavior)
✅ `kapt` → `ksp` (when safe and equivalent)
✅ Explicit type declarations → Type inference (where clear)
"""


def get_logic_preservation_prompt(language: str) -> str:
    """Get language-specific logic preservation prompt."""
    examples_map = {
        "java": JAVA_SAFE_EXAMPLES,
        "groovy": GROOVY_SAFE_EXAMPLES,
        "kotlin": KOTLIN_SAFE_EXAMPLES,
    }

    examples = examples_map.get(language.lower(), "")
    return f"{LOGIC_PRESERVATION_PROMPT}\n\n{examples}"


CHANGE_PROMPT = """
    For each change needed, specify the change type and provide appropriate details:

    **INSERT changes** (adding new code):
    1. Identify the exact line number where new code should be inserted
    2. Provide the new code to insert (leave 'before' empty)
    3. Explain why this addition is necessary for JDK {target_jdk}
    4. Consider placement relative to existing code (imports, dependencies, etc.)

    **UPDATE changes** (modifying existing code):
    1. Identify the exact lines that need modification (start_line to end_line)
    2. Provide both the current code (before) and replacement code (after)
    3. Explain why the change is necessary for JDK {target_jdk}
    4. Ensure the replacement maintains the same functionality with modern syntax

    **DELETE changes** (removing obsolete code):
    1. Identify the exact lines that need removal (start_line to end_line)
    2. Provide the current code to be deleted (leave 'after' empty)
    3. Explain why this code is obsolete or incompatible with JDK {target_jdk}
    4. Ensure removal doesn't break dependencies or required functionality

    **General considerations for all changes:**
    - Consider dependencies between changes (e.g., plugin updates before dependency updates)
    - Maintain proper ordering (imports before usage, declarations before references)
    - Preserve code formatting and indentation style
    - Insert changes should be in the same indentation level as the adjacent codes in the file
    - Update changes should be in the same indentation level as the code it replaces
    - Ensure changes work together as a cohesive set
    - Validate that line numbers are accurate and non-overlapping
    - When suggesting changes, consolidate related modifications into single
        changes when possible. For example, if multiple consecutive lines
        need similar updates, provide ONE change that updates all lines
        together rather than separate changes for each line.
"""

# NOTE: Use this to experiment and fine-tune the responses.
# Prefer to write here than in the upgrader classes' PROMPT to save tokens
EXTRA_PROMPT = "\n\n".join([
    os.getenv("EXTRA_PROMPT_UPGRADERS", ""),

    """
    IMPORTANT:
    - Reference line numbers exactly as they appear in the file (starting from line 1)
    - For Gradle files, use Gradle syntax suggestions
    - For Maven files (pom.xml), use Maven syntax suggestions
    - For .properties files, only suggest property changes
    """,

    # add your own prompts here...
])
