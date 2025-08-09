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
