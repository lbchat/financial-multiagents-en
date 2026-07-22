# Code Style

- Functions do one thing. If you need "and" to describe one, split it into two.
- Variable names describe what they contain. Function names describe what they do.
- No abbreviations. `get_market_features`, not `get_mkt_feat`.
- No commented-out code. Delete it. Git remembers.
- Handle errors explicitly. Never use `except: pass` or silently ignore an exception.
- Files with more than 300 lines must be split into modules.
- Type hints in every function signature.
- Docstrings in public functions—one line in Portuguese describing what the function does.
- Imports in three groups separated by a blank line: stdlib → external → internal.

## Tests
- Every test must exercise the same code path that actual usage will exercise—not merely validate an isolated object in memory. Testing the construction of an object does not replace testing its serialization, persistence, or any transformation that production code actually applies before using it.
