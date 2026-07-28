# Code Patterns

## Standard tool

Tools are ordinary Python functions exposed through LangChain's `@tool`
decorator, but they are not necessarily pure:

- `apply_decision_rules` is a deterministic helper with no external I/O.
- `get_market_features`, `get_sentiment_features`, and `analyze_context` call
  data/model layers that perform external I/O or inference.
- `generate_recommendation` invokes the market and sentiment tools before
  applying the deterministic rules.
- `save_recommendation` and `load_recommendations` perform filesystem I/O.

Language policy for these examples: Portuguese `@tool` docstrings, agent
prompts, runtime exceptions, and machine values are intentional because the
application runtime is Brazilian Portuguese only. Ordinary developer-facing
docstrings and comments use English.

```python
# src/quantumfinance/tools/market_tools.py
from langchain_core.tools import tool
from quantumfinance.features.technical import calculate_indicators
from quantumfinance.data.market_data import fetch_ohlcv

@tool
def get_market_features(ticker: str) -> dict:
    """Retorna preço atual e indicadores técnicos (RSI, MACD, médias móveis, Bollinger) para o ticker informado."""
    data = fetch_ohlcv(ticker)
    return calculate_indicators(data)
```

Rules:
- LangChain `@tool` decorator
- Type hints on all parameters and on the return value
- One-line docstring in Portuguese—the LLM uses it to decide when to call the tool
- Errors handled at the lowest appropriate data boundary and never silently
  swallowed

## Error handling in functions that call external APIs

```python
import pandas as pd
import yfinance as yf


def fetch_ohlcv(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """Fetches OHLCV data from Yahoo Finance for the specified ticker."""
    yf_ticker = f"{ticker}.SA"
    try:
        data = yf.download(
            yf_ticker,
            period=period,
            progress=False,
            auto_adjust=True,
        )
        if data.empty:
            raise ValueError(f"Nenhum dado retornado para {ticker} ({yf_ticker})")
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        return data
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar dados para {ticker}: {e}") from e
```

## LLM configuration through DeepInfra

```python
# src/quantumfinance/config.py
import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv()

def get_llm() -> ChatOpenAI:
    """Returns the configured LLM instance via DeepInfra."""
    api_key = os.getenv("DEEPINFRA_API_KEY")
    if not api_key:
        raise RuntimeError("DEEPINFRA_API_KEY não encontrada. Configure o arquivo .env")
    return ChatOpenAI(
        model="Qwen/Qwen3-235B-A22B-Instruct-2507",
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=SecretStr(api_key),
        temperature=0.1,
    )
```

## Agent node in LangGraph

```python
# src/quantumfinance/agents/market_agent.py
from langgraph.prebuilt import create_react_agent
from quantumfinance.config import get_llm
from quantumfinance.tools.market_tools import get_market_features

MARKET_AGENT_PROMPT = """Você é o MarketAgent do sistema QuantumFinance.

Sua única responsabilidade é coletar dados de mercado e calcular indicadores técnicos.
Nunca emita recomendações de compra ou venda."""


def build_market_agent():
    """Builds the MarketAgent with its registered tools."""
    return create_react_agent(
        model=get_llm(),
        tools=[get_market_features],
        prompt=MARKET_AGENT_PROMPT,
    )
```

The source prompt contains additional PT-BR instructions for immediate tool
use and multi-ticker comparisons. Keep prompts in named constants so their
runtime language and agent responsibility are explicit.

## Structured DecisionAgent output

```python
from pydantic import BaseModel
from enum import Enum

class Recommendation(str, Enum):
    COMPRAR = "COMPRAR"
    VENDER = "VENDER"
    AGUARDAR = "AGUARDAR"

class RecommendationOutput(BaseModel):
    ticker: str
    date: str                    # YYYY-MM-DD format
    recommendation: Recommendation
    confidence: float            # 0.0 to 1.0
    rsi: float
    macd_signal: str
    sentiment_score: float
    sentiment_label: str
    top_headlines: list[str]
    reasoning: str
```

## Validated serialization at the tool boundary

`generate_recommendation` constructs the validated Pydantic model and converts
it to JSON-compatible primitives before returning the tool result:

```python
@tool
def generate_recommendation(ticker: str) -> dict:
    """Gera recomendação fundamentada de COMPRAR, VENDER ou AGUARDAR para o ticker informado."""
    # Market and sentiment collection omitted here; see decision_tools.py.
    output = RecommendationOutput(
        ticker=ticker,
        date=date.today().isoformat(),
        recommendation=Recommendation(decision["recommendation"]),
        confidence=decision["confidence"],
        rsi=rsi,
        macd_signal=macd_signal,
        sentiment_score=sentiment_score,
        sentiment_label=sentiment_label,
        top_headlines=top_headlines[:3],
        reasoning=decision["reasoning"],
    )
    return output.model_dump(mode="json")
```

Always use `mode="json"` at this boundary so `Recommendation` enum members
become plain persisted strings.

## Recommendation persistence

```python
# src/quantumfinance/output/storage.py
import csv
from pathlib import Path

RECOMMENDATIONS_PATH = Path("data/recommendations.csv")

FIELDNAMES = [
    "ticker", "date", "recommendation", "confidence",
    "rsi", "macd_signal", "sentiment_score", "sentiment_label",
    "top_headlines", "reasoning",
]


def save_recommendation(data: dict) -> None:
    """Persists a recommendation in the historical CSV."""
    RECOMMENDATIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    write_header = not RECOMMENDATIONS_PATH.exists()
    with open(RECOMMENDATIONS_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES,
            extrasaction="ignore",
        )
        if write_header:
            writer.writeheader()
        writer.writerow(data)


def load_recommendations() -> list[dict]:
    """Loads the recommendation history from the CSV."""
    if not RECOMMENDATIONS_PATH.exists():
        return []
    with open(RECOMMENDATIONS_PATH, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))
```

## Imports—mandatory order

```python
# 1. stdlib
import os
import csv
from pathlib import Path
from enum import Enum

# 2. Third-party packages
import pandas as pd
import yfinance as yf
from langchain_core.tools import tool

# 3. Internal modules
from quantumfinance.config import get_llm
from quantumfinance.features.technical import calculate_indicators
```
