# Code Patterns

## Standard tool

Every tool is a pure Python function. No side effects and no calls to other agents.

Language policy for these examples: Portuguese `@tool` docstrings, agent prompts, runtime exceptions, and machine values are intentional because the application runtime is Brazilian Portuguese only. Ordinary developer-facing docstrings must be written in English. All fenced examples remain unchanged in this policy-only phase, including obsolete or non-runtime Portuguese content.

```python
# src/quantumfinance/tools/market_tools.py
from langchain_core.tools import tool
from quantumfinance.features.technical import calculate_indicators
from quantumfinance.data.market_data import fetch_ohlcv

@tool
def get_market_features(ticker: str) -> dict:
    """Retorna preço atual e indicadores técnicos para o ticker informado."""
    data = fetch_ohlcv(ticker, period="3mo")
    return calculate_indicators(data)
```

Rules:
- LangChain `@tool` decorator
- Type hints on all parameters and on the return value
- One-line docstring in Portuguese—the LLM uses it to decide when to call the tool
- Exceptions handled explicitly within the function, never silenced

## Error handling in functions that call external APIs

```python
def fetch_ohlcv(ticker: str, period: str = "3mo") -> pd.DataFrame:
    """Coleta dados OHLCV do Yahoo Finance para o ticker informado."""
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data.empty:
            raise ValueError(f"Nenhum dado retornado para {ticker}")
        return data
    except Exception as e:
        raise RuntimeError(f"Erro ao buscar dados para {ticker}: {e}") from e
```

## LLM configuration through DeepInfra

```python
# src/quantumfinance/config.py
import os
from langchain_openai import ChatOpenAI

def get_llm() -> ChatOpenAI:
    """Retorna instância configurada do LLM via DeepInfra."""
    return ChatOpenAI(
        model="Qwen/Qwen2.5-7B-Instruct",
        base_url="https://api.deepinfra.com/v1/openai",
        api_key=os.getenv("DEEPINFRA_API_KEY"),
        temperature=0.1,
    )
```

## Agent node in LangGraph

```python
# src/quantumfinance/agents/market_agent.py
from langgraph.prebuilt import create_react_agent
from quantumfinance.config import get_llm
from quantumfinance.tools.market_tools import get_market_features

def build_market_agent():
    """Constrói o MarketAgent com suas tools registradas."""
    return create_react_agent(
        model=get_llm(),
        tools=[get_market_features],
        prompt="Você é o MarketAgent. Sua única responsabilidade é coletar dados de mercado e calcular indicadores técnicos. Nunca emita recomendações."
    )
```

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
    date: str                    # formato YYYY-MM-DD
    recommendation: Recommendation
    confidence: float            # 0.0 a 1.0
    rsi: float
    macd_signal: str
    sentiment_score: float
    sentiment_label: str
    top_headlines: list[str]
    reasoning: str
```

## Recommendation persistence

```python
# src/quantumfinance/output/storage.py
import csv
from pathlib import Path
from quantumfinance.agents.decision_agent import RecommendationOutput

RECOMMENDATIONS_PATH = Path("data/recommendations.csv")

def save_recommendation(rec: RecommendationOutput) -> None:
    """Persiste uma recomendação no CSV histórico."""
    write_header = not RECOMMENDATIONS_PATH.exists()
    with open(RECOMMENDATIONS_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rec.model_fields.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(rec.model_dump())
```

## Imports—mandatory order

```python
# 1. stdlib
import os
import csv
from pathlib import Path
from enum import Enum

# 2. pacotes externos
import pandas as pd
import yfinance as yf
from langchain_core.tools import tool

# 3. módulos internos
from quantumfinance.config import get_llm
from quantumfinance.features.technical import calculate_indicators
```
