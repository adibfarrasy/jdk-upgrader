class UpgraderConfig:
    SKIP_PATTERNS = [
        # Generated/compiled files
        "build/*",
        "bin/*",
        ".gradle/*",
        "target/*",
        "out/*",

        # Generated source code
        "generated/*",
        "**/generated/**",
        "gen/*",
        "**/gen/**",

        # Build artifacts
        "*.class",
        "*.jar",
        "*.war",
        "*.ear",

        # IDE files
        ".idea/*",
        ".vscode/*",
        "*.iml",

        # Version control
        ".git/*",

        # Logs and temporary files
        "logs/*",
        "*.log",
        "tmp/*",
        "temp/*",
    ]

    MAX_BLOCK_LINES = 20

    UPGRADE_KEYWORDS_JAVA = [
        # JDK 9-11: Collection Factory Methods
        r"Arrays\.asList\(",
        r"Collections\.unmodifiableList\(",
        r"Collections\.emptyList\(",
        r"Collections\.singletonList\(",

        # JDK 11: String Methods
        r"\.trim\(\)",
        r"\.isEmpty\(\)",
        r"StringUtils\.isBlank\(",

        # JDK 14: Switch Expressions
        r"switch\s*\([^)]+\)\s*\{",
        r"case\s+[^:]+:\s*break;",

        # JDK 14: Pattern Matching for instanceof
        r"instanceof\s+\w+\s*\)\s*\{",
        r"\(\s*\(\w+\)",  # Cast after instanceof

        # JDK 15: Text Blocks
        r'"\s*\+\s*"',           # String concatenation
        r'"\s*\\n\s*"',          # Newline in strings
        r'String\.format\(',      # String formatting

        # JDK 16: Records (detect POJO patterns)
        r"private\s+final\s+\w+",
        r"public\s+\w+\s+get\w+\(\)",
        r"@Override\s+public\s+boolean\s+equals",
        r"@Override\s+public\s+int\s+hashCode",

        # JDK 17: Sealed Classes
        r"public\s+(abstract\s+)?class\s+\w+",
        r"extends\s+\w+",

        # JDK 19-21: Virtual Threads
        r"Executors\.newFixedThreadPool\(",
        r"new\s+Thread\(",
        r"Thread\.start\(\)",

        # Optional Improvements
        r"if\s*\([^)]*!=\s*null\)",
        r"if\s*\([^)]*==\s*null\)",

        # Stream API Opportunities
        r"for\s*\([^)]*:\s*\w+\)",
        r"\.size\(\)\s*>\s*0",
        r"\.length\s*>\s*0",

        # Try-with-resources
        r"try\s*\{[^}]*\.close\(\)",
        r"finally\s*\{[^}]*\.close\(\)",

        # Deprecated/Removed APIs
        r"sun\.misc\.",
        r"com\.sun\.",
        r"java\.security\.AccessController",
        r"SecurityManager",
        r"System\.getSecurityManager",

        # HTTP Client (JDK 11)
        r"HttpURLConnection",
        r"URLConnection",

        # Time API (JDK 8 had it, but patterns for old usage)
        r"java\.util\.Date",
        r"SimpleDateFormat",
        r"Calendar\.",
    ]

    UPGRADE_KEYWORDS_GROOVY = [
        # Build Script Modernization
        r"compile\s+['\"]",
        r"testCompile\s+['\"]",
        r"runtime\s+['\"]",
        r"testRuntime\s+['\"]",

        # Plugin Application
        r"apply\s+plugin:",

        # Groovy Version Compatibility
        r"groovy-all",
        r"org\.codehaus\.groovy",

        # Configuration Methods
        r"configurations\s*\{",
        r"sourceSets\s*\{",

        # Gradle Wrapper
        r"gradleVersion\s*=",

        # Task Configuration
        r"task\s+\w+\s*\(",

        # Java Compatibility
        r"sourceCompatibility\s*=",
        r"targetCompatibility\s*=",

        # Compiler Options
        r"compileJava\s*\{",
        r"compileGroovy\s*\{",

        # Dependencies Block Patterns
        r"dependencies\s*\{",
        r"implementation\s*\(",
        r"api\s*\(",
        r"testImplementation\s*\(",

        # Repository Patterns
        r"repositories\s*\{",
        r"mavenCentral\(\)",
        r"jcenter\(\)",  # Deprecated

        # Publishing
        r"publishing\s*\{",
        r"maven\s*\{",
    ]

    UPGRADE_KEYWORDS_KOTLIN = [
        # JVM Target
        r"jvmTarget\s*=\s*['\"]1\.[8-9]['\"]",
        r"jvmTarget\s*=\s*['\"]11['\"]",

        # Kotlin Version
        r"kotlin_version\s*=",
        r"org\.jetbrains\.kotlin",

        # Coroutines vs Virtual Threads
        r"runBlocking\s*\{",
        r"suspend\s+fun",
        r"GlobalScope\.launch",

        # Build Script Patterns
        r"kotlin\s*\(",
        r"kapt\s*\(",

        # Compiler Options
        r"kotlinOptions\s*\{",
        r"compileKotlin\s*\{",

        # Plugin Application
        r"kotlin\(['\"]jvm['\"]",
        r"kotlin\(['\"]multiplatform['\"]",

        # Dependencies
        r"kotlin-stdlib",
        r"kotlin-reflect",

        # API Level
        r"apiVersion\s*=",
        r"languageVersion\s*=",
    ]
