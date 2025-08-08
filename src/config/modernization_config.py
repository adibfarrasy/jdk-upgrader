class ModernizationConfig:
    SKIP_PATTERNS = ["*Test.java", "*Spec.groovy", "generated/*"]
    MAX_BLOCK_LINES = 20


# TODO: update keywords for java
MODERNIZATION_KEYWORDS_JAVA = [r"instanceof\s+\w+", r"switch\s*\(", r"StringBuilder"]

# TODO: update keywords for groovy
MODERNIZATION_KEYWORDS_GROOVY = [r"compile\s+", r"testCompile", r"implementation\s+"]

# TODO: update keywords for kotlin
MODERNIZATION_KEYWORDS_KOTLIN = [r"jvmTarget\s*=", r"runBlocking\s*{", r"suspend\s+fun"]
