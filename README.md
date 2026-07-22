# QuantumFinance AI Agent

Multi-agent system that recommends **COMPRAR / VENDER / AGUARDAR** (the literal application values for buy / sell / hold) for Brazilian stocks by combining technical indicators with news sentiment analysis—with an auditable natural-language rationale rather than a black box.

## The problem and the solution

Deciding whether to buy, sell, or hold a stock requires combining two types of information that usually live in separate places: **what the numbers say** (price, RSI, MACD, moving averages) and **what is being reported** about the company (quarterly results, management changes, regulatory risk). Doing this manually every day for several stocks does not scale.

The solution here is a **multi-agent system**: an orchestrator determines whether the user's question calls for a complete recommendation or only a specific data point, then directs the work to specialized agents—one that looks only at the market, one that looks only at sentiment, and one that combines both into a final recommendation with an explanation of the underlying logic. Each recommendation is recorded in a CSV file together with all the indicators that motivated it, making it possible to revisit and audit why the agent made a given decision.

The system covers 4 B3-listed stocks: **PETR4 · VALE3 · BBAS3 · ITUB4**.

## Language policy

Repository documentation is written in English for international readability. The working application intentionally operates only in Brazilian Portuguese: user questions, agent answers and recommendation explanations, Gradio interface text, prompts, runtime messages, demo interactions, and financial-language processing remain in PT-BR. This aligns the runtime with Brazilian Portuguese financial-news sources and FinBERT-PT-BR. English conversational input and output are not claimed as supported or validated.

## Architecture

3 specialized agents (`MarketAgent`, `SentimentAgent`, `DecisionAgent`) plus a LangGraph orchestrator with **hybrid** coordination:

- **Fixed pipeline** (`pipeline_market → pipeline_sentiment → pipeline_decision`) for complete recommendations—the tools are called directly in Python, without going through the LLM, ensuring that no step is ever skipped and that the wrong tool is not called. The LLM (`DecisionAgent`) is used only at the end to narrate the result that has already been calculated.
- **Dynamic routing** (`market_node`, `sentiment_node`) for specific questions ("qual o RSI de VALE3?", meaning "what is VALE3's RSI?")—here, the LLM genuinely decides which tools to call, using a true ReAct approach.

See the complete diagram (agent flow + backtest pipeline) in [`docs/architecture.md`](docs/architecture.md). Detailed decisions and trade-offs are documented in [`docs/decisions.md`](docs/decisions.md).

## Running locally

### Prerequisites

- Python 3.11+
- A [DeepInfra](https://deepinfra.com/) account with an API key (free credits cover the demo)
- *(Optional—only to reproduce the backtest with real historical sentiment)* a Google Cloud account with BigQuery enabled and the `gcloud` CLI authenticated

### Installation

```powershell
git clone <url-do-repositorio>
cd ENTREGA_MULTI-AGENTS
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

### Configuration

```powershell
Copy-Item .env.example .env
# edit .env and fill in DEEPINFRA_API_KEY
```

To reproduce the backtest with real historical sentiment (optional and not required for the main interface):

```powershell
gcloud auth application-default login
```

### Running the conversational interface

```powershell
python src/quantumfinance/app/gradio_app.py
```

The interface opens at `http://localhost:7860`. Because the application runtime is intentionally Brazilian Portuguese only, the example questions remain in Portuguese: "Qual a recomendação para PETR4 hoje?" ("What is today's recommendation for PETR4?"), "Compare os indicadores de VALE3 e PETR4" ("Compare the indicators for VALE3 and PETR4"), and "Qual o sentimento das notícias sobre BBAS3?" ("What is the sentiment of news about BBAS3?"). The English text in parentheses explains their meaning only; it is not claimed as supported or validated conversational input.

### Running tests and quality checks

```powershell
pytest tests/ -v       # 20 tests, critical functions
mypy src/               # types
ruff check src/         # lint
```

### Reproducing the backtest (optional)

```powershell
python scripts/run_backtest_gdelt.py
```

## Backtest results

Historical simulation over the last ~90 trading days for the 4 tickers, comparing each day's recommendation with the actual return over the next 5 trading sessions and with the Ibovespa over the same period. The backtest **does not call the LLM or FinBERT**—it uses only the deterministic decision function (`apply_decision_rules`) to isolate the quality of the technical+sentiment signal from the quality of the natural-language narrative.

| Mode | Rows | Directional accuracy | Beat Ibovespa | Sentiment |
|---|---|---|---|---|
| Placeholder (fixed neutral sentiment) | 229 | ~40% | ~52% | `sentiment_score=0.5` always |
| GDELT/BigQuery (real historical sentiment) | 243 | ~42% | ~53.8% | 100% real, 0% fallback |

*(Exact values vary slightly between runs because the backtest window is always "the last 90 days"—rolling rather than fixed. The numbers above are representative of what the `04_backtest_and_evaluation.ipynb` notebook produces.)*

**An honest reading of the numbers:** accuracy of ~40-42% on a 3-class decision (COMPRAR/VENDER/AGUARDAR, random baseline ~33%) is above chance, but this is not a validated signal for real-world use—it is evidence that the logic is sound, not that it is profitable. Beating the Ibovespa ~52-54% of the time is also close to a coin toss. The more concrete improvement from using real sentiment (GDELT) instead of the neutral placeholder was small and concentrated on a few specific days (see the notebook), because news sentiment remains in a neutral range most of the time and does not change the decision (`apply_decision_rules` allows sentiment to have an effect only when the score rises above 0.6 or falls below 0.4).

For full details, charts, and a side-by-side comparison of the two modes, see [`notebooks/04_backtest_and_evaluation.ipynb`](notebooks/04_backtest_and_evaluation.ipynb).

## Key architectural decisions

- **Deterministic pipeline in the recommendation flow**—chaining 3 ReAct agents while passing the accumulated conversation did not work reliably (the LLM saw a conversation that "already looked answered" and did not call the tool). The solution was to call the tools directly in Python on the main path, with the LLM used only for narration.
- **Historical sentiment through Google BigQuery**—the original GDELT client using the REST API had severe rate limiting (~30min for 3 weeks of data). It was replaced with BigQuery, which accesses the same public GDELT dataset without that limitation and completes the full backtest in minutes instead of hours.
- **FinBERT-PT-BR for sentiment**—a model specialized in Portuguese financial sentiment, used only for inference (without fine-tuning) in the agent's real-time path.

The full rationale for each decision, including the accepted trade-offs, is available in [`docs/decisions.md`](docs/decisions.md).

## Known limitations

- **Real-time sentiment depends on RSS, which is volatile by nature.** News coverage for a specific ticker at a given time depends on what the feeds have published in recent hours—there may be nothing relevant, in which case the system falls back to neutral (`sentiment_score=0.5`) without explicitly notifying the user.
- **Historical backtest sentiment (GDELT) is a general media score, not a specialized financial score**—unlike the FinBERT-PT-BR model used by the real-time agent. It is a reasonable proxy for the backtest, not the same signal used in production.
- **Sequential latency in the BigQuery backtest**—one query per ticker/day combination (243 calls for 90 days × 4 tickers, ~25min). It works well at the current volume, but it is not the most efficient approach; batch queries would reduce this to a few calls (see Next steps).
- **Keyword matching uses exact substrings rather than semantic matching**—a headline may match a ticker through a generic word (for example, "juros" or "Selic") without actually being about that company. The full headline remains visible for auditing, but the filter itself cannot distinguish genuine relevance from a coincidental term match.
- **The fixed pipeline is less "agentic" in the strict sense**—the main recommendation path does not let the LLM decide the tool sequence; this is a deliberate trade-off for reliability, not an overlooked technical limitation (see the decision above).
- **Backtest accuracy is a proof of concept, not a validated signal**—see "Backtest results" above.
- **Dependence on external services**—DeepInfra (LLM), Yahoo Finance, RSS feeds, and BigQuery must be available; the system has fallbacks (neutral sentiment and user-friendly error messages in Gradio), but it does not work entirely offline.

## Next steps

- **Batch queries in BigQuery and bulk downloads in yfinance**—replace the hundreds of sequential backtest calls with a single aggregate query (`GROUP BY ticker, date`) and a single `yf.download` per ticker, eliminating most network round trips.
- **Integration with CVM data**—fundamentals and regulatory disclosures for the monitored companies, supplementing news sentiment with official structured data.
- **Integration with the Brazilian Central Bank's Focus Report**—market expectations for the Selic rate, inflation, and exchange rates as additional macroeconomic context for the decision.
- **Context Router Agent**—an agent that dynamically decides which thematic areas (political, environmental, regulatory) are relevant to each ticker before retrieving sentiment, instead of using the current fixed set of keywords.

## Stack

Python 3.11+ · LangGraph · DeepInfra (Qwen3-235B-A22B-Instruct) · FinBERT-PT-BR · yfinance · feedparser · pandas-ta · Google BigQuery · Gradio · pytest/ruff/mypy

## Project structure

```
src/quantumfinance/
├── data/          # price, news, and historical sentiment collection (GDELT/BigQuery)
├── features/      # technical indicators, sentiment, backtest targets
├── agents/        # MarketAgent, SentimentAgent, DecisionAgent, orchestrator
├── tools/         # tools registered with the agents
├── output/        # recommendation persistence
├── backtesting/   # historical simulation and metrics
└── app/           # Gradio interface
tests/             # pytest for critical functions
notebooks/         # visual validation and end-to-end demo
docs/              # decisions, progress, coding standards, architecture
```
