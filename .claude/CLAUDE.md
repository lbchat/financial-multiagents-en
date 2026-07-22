# QuantumFinance AI Agent

Multi-agent system for recommending Brazilian stocks (COMPRAR / VENDER / AGUARDAR) by combining technical indicators and news sentiment analysis, with an auditable rationale.

## Stack
- Python 3.11+, LangGraph, DeepInfra API (Qwen/Qwen3-235B-A22B-Instruct-2507)
- FinBERT-PT-BR—Portuguese financial sentiment
- yfinance + feedparser—market data and RSS news
- pandas-ta—technical indicators (never TA-Lib)
- Gradio—conversational interface
- pytest + ruff + mypy—tests, linting, and types

## Environment
- Windows 11, PowerShell—use PowerShell commands, not bash

## Language policy
- English is the repository's engineering and documentation language and should be used for repository, architecture, planning, and development documentation; source-code comments; test comments and explanatory documentation; notebook Markdown and developer comments; ordinary developer-facing docstrings; and other non-runtime annotations.
- Brazilian Portuguese must remain the language of user questions; agent answers and recommendation explanations; Gradio interface text and example questions; runtime warnings, errors, status, and progress messages; agent, router, and recommendation-narration prompts; LLM-visible tool descriptions and `@tool` docstrings; manual agent-test prompts and demo interactions; financial-news keywords and aliases; FinBERT inputs and label mappings; contextual keyword maps; and future persisted recommendation reasoning.
- Never claim that English runtime input or output is supported or validated.
- Ordinary developer-facing docstrings must be written in English. Docstrings exposed to LangChain or an LLM, or reused as runtime help, prompt content, tool-selection guidance, or user-visible text, must remain in Brazilian Portuguese.
- When uncertain whether a docstring is LLM-visible or runtime-visible, preserve it in Portuguese and flag it for review.
- Preserve `COMPRAR`, `VENDER`, `AGUARDAR`, `POSITIVO`, `NEGATIVO`, and `NEUTRO`, as well as routing labels, schema keys, CSV fields, dictionary keys, DataFrame columns, persisted values, Portuguese keyword lists, model mappings, identifiers, filenames, and paths.

## Structure
- `src/quantumfinance/data/`—price and news collection
- `src/quantumfinance/features/`—technical indicators and sentiment
- `src/quantumfinance/agents/`—orchestrator and specialized agents
- `src/quantumfinance/tools/`—tools registered with the agents
- `src/quantumfinance/output/`—formatting and persistence
- `src/quantumfinance/app/`—Gradio
- `tests/`—pytest focused on critical functions
- `data/`—recommendations.csv and sessions.json (generated at runtime)

## Commands
- Interface: `python src/quantumfinance/app/gradio_app.py`
- Tests: `pytest tests/ -v`
- Lint: `ruff check src/`
- Types: `mypy src/`

## Verification after every change
1. `mypy src/`—fix type errors
2. `pytest tests/ -v`—fix failing tests
3. `ruff check src/`—fix lint issues

## Do not
- Never use TA-Lib—use pandas-ta
- Never hard-code tickers—use `TICKERS` from `config.py`
- Never hard-code API keys—use `.env` through python-dotenv
- Never put business logic in the agents—it belongs in the tools and in `features/`
- Never shuffle backtest data—always use chronological order
- Never use a plain model_dump() on RecommendationOutput—always use model_dump(mode="json") to ensure correct serialization of the Recommendation enum.

## References
- Architecture and decisions: `docs/decisions.md`
- Code patterns and tool examples: `docs/patterns.md`
- Current status and next stages: `docs/progress.md`
- Code style: `docs/code-style.md`
