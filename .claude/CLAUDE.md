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
