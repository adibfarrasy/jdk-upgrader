TODOs:
	src/config/modernization_config.py:6:	update keywords for java
	src/config/modernization_config.py:9:	update keywords for groovy
	src/config/modernization_config.py:12:	update keywords for kotlin
	src/build_fixers/error_handler.py:23:	Define which error types are actionable
	src/build_fixers/error_handler.py:56:	Implement actual Gradle execution
	src/build_fixers/error_handler.py:66:	Parse result.stdout and result.stderr for errors
	src/build_fixers/error_handler.py:72:	Handle build timeout
	src/build_fixers/error_handler.py:82:	Handle other build failures
	src/build_fixers/error_handler.py:115:	Implement regex parsing patterns
	src/build_fixers/error_handler.py:167:	Group errors by file
	src/build_fixers/error_handler.py:171:	Check attempt limit
	src/build_fixers/error_handler.py:176:	Get code context for errors
	src/build_fixers/error_handler.py:180:	Generate LLM prompt and get suggested fix
	src/build_fixers/error_handler.py:205:	Implement grouping logic
	src/build_fixers/error_handler.py:230:	Implement context extraction
	src/build_fixers/error_handler.py:257:	Implement LLM fix generation
	src/build_fixers/error_handler.py:311:	Run build
	src/build_fixers/error_handler.py:318:	Filter actionable errors
	src/build_fixers/error_handler.py:328:	Get suggested fixes
	src/build_fixers/error_handler.py:335:	Review fixes with human
	src/reviewer.py:39:	Implement full review workflow
	src/reviewer.py:55:	Add file stats (size, last modified, etc.)
	src/reviewer.py:60:	Implement proper diff visualization
	src/reviewer.py:79:	Expand language detection
	src/reviewer.py:92:	Add more options (view original, compare side-by-side)
	src/reviewer.py:103:	Add backup functionality
	src/reviewer.py:115:	Implement interactive editing
	src/generators/patch_generator.py:36:	Implement diff generation
	src/generators/patch_generator.py:65:	Implement patch application
