# Code Style

- Functions do one thing. If you need "and" to describe one, split it into two.
- Variable names describe what they contain. Function names describe what they do.
- No abbreviations. `get_market_features`, not `get_mkt_feat`.
- No commented-out code. Delete it. Git remembers.
- Handle errors explicitly. Never use `except: pass` or silently ignore an exception.
- Files with more than 300 lines must be split into modules.
- Type hints in every function signature.
- English should be used for source-code comments, test comments and explanatory documentation, notebook Markdown and developer comments, and other non-runtime annotations.
- Ordinary developer-facing docstrings must be written in English.
- `@tool` docstrings and any docstring exposed to LangChain or an LLM, or reused as runtime help, prompt content, tool-selection guidance, or user-visible text, must remain in Brazilian Portuguese.
- Runtime-visible text—including prompts, questions, answers, explanations, interface text, warnings, errors, status messages, and manual agent-test inputs—must remain in Brazilian Portuguese.
- When uncertain whether a docstring is LLM-visible or runtime-visible, preserve it in Portuguese and flag it for review.
- Imports in three groups separated by a blank line: stdlib → external → internal.

## Tests
- Every test must exercise the same code path that actual usage will exercise—not merely validate an isolated object in memory. Testing the construction of an object does not replace testing its serialization, persistence, or any transformation that production code actually applies before using it.
