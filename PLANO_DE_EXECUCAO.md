# Execution Plan — QuantumFinance AI Agent

---

## Part 1 — Stage-by-Stage Execution Plan

### Stage 0 — Project foundation

Before writing a single line of agent code, prepare the foundation. This may seem obvious, but it is where most academic projects start going off track.

- Create the repository on GitHub (public, with an initial README even if minimal)
- Configure a lean Python environment with `pyproject.toml` or `requirements.txt`—only what you know you will use
- Create `.env.example` with the required variables: `DEEPINFRA_API_KEY`
- Define the minimum folder structure without creating empty folders "for the future"
- Place `CLAUDE.md` at the root and create the `docs/` folder with the four context files
- **Validate the LLM before writing any agent code:** make a simple call to Qwen 2.5 7B through DeepInfra with a question that requires tool calling, and confirm that the response format is compatible with LangGraph. If it is inconsistent, switch to Llama 3.1 8B—this changes only one line in `config.py`.

**Exit criterion:** `python -c "import quantumfinance"` works, the repository is on GitHub, the README explains what the project does in 3 paragraphs, and a test call to Qwen 2.5 7B through DeepInfra returned a well-formatted tool call.

---

### Stage 1 — Market-data pipeline

The objective is to have a function that receives a ticker and returns prices + technical indicators ready for use. No agent yet, no LLM, and no AI of any kind.

- Implement collection through `yfinance` for one ticker, returning OHLCV
- Calculate the indicators required by the course: RSI, MACD, SMA, EMA, Bollinger Bands, Volume
- Use `pandas-ta`—never TA-Lib (a problematic native dependency on Windows)
- Validate visually in a notebook: plot price + indicators and check whether they make sense

**Exit criterion:** a `get_market_features("PETR4")` function that returns a dictionary with the current price and calculated indicators, plus a notebook containing the validated charts.

---

### Stage 2 — News and sentiment pipeline

News collection and sentiment classification with FinBERT-PT-BR.

- Collect RSS feeds through `feedparser` (InfoMoney, Valor Econômico, Reuters, B3)
- Filter by keywords associated with the ticker (Petrobras, PETR4, petróleo, combustíveis…)
- Load the FinBERT-PT-BR model through HuggingFace `transformers`—inference only, without fine-tuning
- Classify the sentiment of each article (POSITIVO / NEGATIVO / NEUTRO + confidence score)
- Aggregate: average sentiment score and count of the latest N articles

**Exit criterion:** a `get_sentiment_features("PETR4")` function that returns a dictionary containing recent average sentiment, the number of articles analyzed, and the 3 most relevant headlines with their scores.

---

### Stage 3 — Building the MVP agent

Once the functions from stages 1 and 2 are working, turning them into tools and assembling the agent is straightforward.

- Create 3 tools: `get_market_features`, `get_sentiment_features`, `generate_recommendation`
- Implement the LangGraph graph with the 3 specialized agents + orchestrator
- Use a hybrid orchestrator pattern: fixed pipeline (Market → Sentiment → Decision) for complete recommendations and dynamic routing for specific questions
- Define each agent's system prompt with a single, explicit responsibility
- Implement basic session memory for multi-turn conversations
- Ensure that the reasoning (Chain-of-Thought) is recorded in a structured format
- DecisionAgent output: structured JSON validated against the `Recommendation(COMPRAR, VENDER, AGUARDAR)` enum

**Exit criterion:** you ask in the terminal using the Portuguese input "qual a recomendação para PETR4 hoje?" (meaning "what is today's recommendation for the stock?") and the agent responds with COMPRAR/VENDER/AGUARDAR + a rationale based on real data collected at that moment.

---

### Stage 4 — Expansion to the 4 tickers

Once the agent is working for PETR4, generalizing it is straightforward. The challenge is to avoid introducing bugs during the expansion.

- Parameterize every function for any ticker
- Test each case individually—VALE3 behaves differently from BBAS3, which may reveal bugs
- Ensure that `TICKERS = ["PETR4", "VALE3", "BBAS3", "ITUB4"]` in `config.py` is the single source of truth
- Validate that the agent handles comparative questions well using the Portuguese input "compare VALE3 e PETR4 hoje" (meaning "compare the two stocks today")

**Exit criterion:** the agent responds correctly for all 4 tickers and maintains the quality of its rationales across all of them.

---

### Stage 5 — Conversational interface (Gradio)

Give the project a face. Gradio turns the agent into something demonstrable and suitable for recording.

- Minimum interface: question field + response area + conversation history
- Show the agent's reasoning in a collapsible section (CoT transparency)
- Predefined example buttons using the Portuguese inputs: "Recomendação para PETR4" (meaning "Recommendation for the stock"), "Compare VALE3 e BBAS3" (meaning "Compare the two stocks"), "Qual o sentimento atual de ITUB4?" (meaning "What is the stock's current sentiment?")

**Exit criterion:** a navigable browser demo that can be recorded in a short portfolio video.

---

### Stage 6 — Backtest and recommendation logging

This is where the project moves from a "functional agent" to an "evaluable agent." It is what makes the strongest impression in both academic evaluation and a portfolio.

- Implement historical simulation: run the agent with data from every trading day over the last 6-12 months
- For each day, record the planned fields in `data/recommendations.csv`: data, ticker, recomendação, confiança, indicadores, sentimento, raciocínio (date, ticker, recommendation, confidence, indicators, sentiment, reasoning)
- Compare performance against buy-and-hold and the Ibovespa
- Calculate metrics: directional accuracy, cumulative return, simplified Sharpe ratio

**Exit criterion:** a backtest notebook with comparative charts and a metrics table.

---

### Stage 7 — Final documentation and delivery

Documentation is where good projects become excellent portfolio projects.

- Complete README: the problem, the solution, architecture, how to run it, limitations, next steps
- Demonstration notebook that orchestrates everything from beginning to end
- Short video (2-3 min) showing the agent in operation
- Architecture diagram in Mermaid or Excalidraw
- Honest list of limitations—demonstrates technical maturity

**Exit criterion:** someone opening the repository can understand the project in 5 minutes and run it locally in 15.

---

## Part 2 — Bonus Idea Bank

Implement only after Stage 5 has been completed, in order of portfolio priority.

### 🥇 1. Asset Context Map + Context Router Agent

**What it is:** an asset-specific contextual mapping system with thematic areas (political, environmental, social, regulatory) and a routing agent that directs news searches to the appropriate sources and keywords for each area.

**When to incorporate it:** after Stage 5 and before the backtest. Implement it for PETR4 first.

**Why it is valuable for a portfolio:** it is the most original idea in the plan. Almost no one will think of it. It becomes a useful story in a technical interview: *"I realized that generic sentiment was losing sector-specific context, so I built a contextual routing system..."*. It demonstrates product and architecture thinking, not just execution.

---

### 🥈 2. Robust comparative backtest

**What it is:** a deeper version of the Stage 6 backtest with walk-forward validation, analysis by market regime (bull vs. bear), and maximum drawdown.

**When to incorporate it:** after Stage 6, as a natural extension.

**Why it is valuable for a portfolio:** quantitative rigor is rare in agent projects. Most stop at "the agent works." Those who validate seriously stand out.

---

### 🥉 3. Analysis by contextual areas

**What it is:** a contextual sentiment layer beyond direct financial sentiment—political, environmental, social, and regulatory. A natural implementation once the Context Router exists.

**When to incorporate it:** immediately after the Asset Context Map. Start with 2 areas per ticker, not 9.

**Why it is valuable for a portfolio:** it completes the project's intellectual thesis and provides rich material for interview discussions—it involves clear trade-offs between precision vs. coverage and noise vs. signal.

---

### 4. Long-term agent memory

**What it is:** the agent remembers previous recommendations and relevant past events, injecting that context into future calls through a JSON file or SQLite.

**When to incorporate it:** after Stage 4.

**Why it is valuable for a portfolio:** memory is one of the most widely discussed topics in agent systems today. It demonstrates an understanding of the lifecycle of an agent in production.

---

### 5. Supervised model using historical recommendations

**What it is:** after the backtest generates hundreds of recommendations with features and actual outcomes, train a simple model (Random Forest or Logistic Regression) to learn which combinations of features predict good recommendations.

**When to incorporate it:** after Stage 6, as a calibration layer for DecisionAgent.

**Why it is valuable for a portfolio:** it demonstrates integration between agents and classical ML—a rare and valued combination. It closes the intellectual loop of the original plan in a solid way.

---

### 6. Automated alerts (Telegram)

**What it is:** the agent runs daily through GitHub Actions and sends recommendations by Telegram message.

**When to incorporate it:** after the academic delivery, as a portfolio extension.

**Why it is valuable for a portfolio:** it turns the academic project into a real, demonstrable product. *"It sends me messages every day"* is a powerful statement in an interview.

---

### 7. Cloud persistence (Azure Blob Storage)

**What it is:** save recommendation CSVs, charts, and logs in Azure using the available credits.

**When to incorporate it:** after Stage 6.

**Why it is valuable for a portfolio:** it adds Azure to the project's scope, which is useful for HR screening. A simple implementation with a visible result in the repository.

---

### 8. Portfolio comparison by risk profile

**What it is:** the agent receives a profile (conservador, moderado, agressivo—meaning conservative, moderate, aggressive) and creates a suggested allocation among the 4 tickers.

**When to incorporate it:** only if time remains after all previous stages.

**Why it is valuable for a portfolio:** it demonstrates product and UX thinking. More relevant to applied AI roles than research roles.

---

### 9. Experimental Deep Learning (LSTM / temporal Transformer)

**What it is:** a time-series model for predicting price direction.

**When to incorporate it:** leave it for a future project, outside the scope of this delivery.

**Why it is listed anyway:** it was part of the original plan. The concrete recommendation is not to include it—with 4 assets, the risk of overfitting is high and explainability decreases, which would hurt the academic evaluation.
