# Architecture

Two independent parts: the **real-time agent** (LangGraph orchestrator behind the Gradio interface) and the **historical backtest** (a pure Python script without an LLM). They share the same technical indicators and decision logic (`apply_decision_rules`), but they run separately—the backtest never calls the agent, and the agent never calls the backtest.

## Real-time agent

The orchestrator classifies each question into one of five intent tokens: `market`, `sentiment`, `diagnostic`, `context`, or `recommendation`. The corresponding graph destinations are `market_node`, `sentiment_node`, `diagnostic_node`, `context_node`, and `pipeline_market`. The `recommendation` intent—and any unrecognized router response as a fallback—enters the complete **fixed pipeline**. The four question-specific destinations invoke ReAct agents; `context_node` constructs its ticker-specific agent per request.

```mermaid
flowchart TD
    U([User]) -->|question| ROUTE{route_intent<br/>LLM classifies the intent}

    ROUTE -->|"market"| MNODE[market_node<br/>MarketAgent · ReAct]
    ROUTE -->|"sentiment"| SNODE[sentiment_node<br/>SentimentAgent · ReAct]
    ROUTE -->|"diagnostic"| DNODE[diagnostic_node<br/>DiagnosticAgent · multi-tool ReAct]
    ROUTE -->|"context"| CNODE[context_node<br/>ticker-specific ContextRouterAgent · ReAct]
    ROUTE -->|"recommendation or fallback"| PM[pipeline_market]

    MNODE --> RESP1([Response])
    SNODE --> RESP2([Response])
    DNODE --> RESP4([Response])
    CNODE --> RESP5([Response])

    PM -->|"calls tool directly in Python,<br/>without letting the LLM decide"| PS[pipeline_sentiment]
    PS -->|"calls tool directly in Python,<br/>without letting the LLM decide"| PD[pipeline_decision]
    PD -->|"DecisionAgent narrates the<br/>already calculated result<br/>in natural language"| RESP3([Response])
    PD --> CSV[(data/recommendations.csv)]

    MNODE -.uses.-> T1[[get_market_features]]
    PM -.uses.-> T1
    SNODE -.uses.-> T2[[get_sentiment_features]]
    PS -.uses.-> T2
    DNODE -.uses.-> T1
    DNODE -.uses.-> T2
    DNODE -.uses.-> T3
    CNODE -.uses.-> T4[[analyze_context]]
    PD -.uses.-> T3[[generate_recommendation]]

    T1 --> D1[(yfinance + pandas-ta<br/>RSI, MACD, moving averages, Bollinger)]
    T2 --> D2[(feedparser RSS + FinBERT-PT-BR<br/>Portuguese-language sentiment)]
    T3 --> D3[apply_decision_rules<br/>RSI + MACD + sentiment → COMPRAR/VENDER/AGUARDAR]
    T3 -.collects current inputs through.-> T1
    T3 -.collects current inputs through.-> T2
    T4 --> D4[(context_map.yaml + RSS + FinBERT-PT-BR<br/>sentiment grouped by thematic sphere)]
```

**Why hybrid:** the fixed pipeline ensures that a complete recommendation never fails because the LLM "forgets" to call a tool or hallucinates a result without real data—this happened during development (see `docs/progress.md`) when the 3 steps were chained as ReAct agents passing along the accumulated conversation. Dynamic routing for market, sentiment, diagnostic, and contextual questions receives the original question and can use ReAct. `DiagnosticAgent` may call all three recommendation-related tools, while `ContextRouterAgent` calls `analyze_context` using the ticker's configured spheres.

## Historical backtest

It runs outside the orchestrator, without an LLM or FinBERT, and uses only the pure decision function, iterating through each trading day in chronological order (never shuffled, to avoid introducing look-ahead bias).

```mermaid
flowchart LR
    RUN[run_backtest] --> GHF[get_historical_features<br/>yfinance, close from the trading day<br/>before the date—never the same day]
    RUN --> SENT{use_gdelt?}
    SENT -->|True, default| FGS[fetch_gdelt_sentiment<br/>BigQuery: gdelt-bq.gdeltv2.gkg_partitioned]
    SENT -->|False| NEUTRO[sentiment_score = 0.5 fixed]

    GHF --> ADR[apply_decision_rules]
    FGS --> ADR
    NEUTRO --> ADR

    ADR --> GFR[get_forward_return + get_ibovespa_return<br/>actual return over the next 5 trading sessions]
    GFR --> CSV2[(data/backtest_results*.csv)]
```

**Why no LLM:** a natural-language narrative adds no value when run hundreds of times in a historical loop—the purpose of the backtest is to measure signal quality (RSI + MACD + sentiment), not explanation quality.

The decisions and trade-offs behind each choice above (deterministic pipeline, migration to BigQuery, protection against look-ahead bias) are detailed in [`decisions.md`](decisions.md).
