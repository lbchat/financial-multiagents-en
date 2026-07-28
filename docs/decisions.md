# Architectural Decisions

## Agent architecture
**Current decision:** five agent roles plus a LangGraph orchestrator:
`MarketAgent`, `SentimentAgent`, `DecisionAgent`, `DiagnosticAgent`, and
`ContextRouterAgent`.
**Rationale:** the original three-role MVP covered market data, sentiment, and
recommendation. Post-delivery work added an investigative role and a
ticker-specific contextual role without changing the responsibilities of the
original three.
**Implementation:** all five builders use `create_react_agent(..., prompt=...)`.
`ContextRouterAgent` is built per request because its prompt contains the
ticker's configured spheres.

## Orchestrator coordination
**Decision:** hybrid pattern—a fixed pipeline for complete recommendations and dynamic routing for specific questions.
**Rationale:** the fixed pipeline ensures reliability in the primary use case. Routing makes the conversational interface fluid and efficient.
**Implementation:** the first node classifies the question as `market`,
`sentiment`, `diagnostic`, `context`, or `recommendation`. Those outcomes route
to `market_node`, `sentiment_node`, `diagnostic_node`, `context_node`, or
`pipeline_market`, respectively; an unrecognized router response also falls
back to `pipeline_market`.

## Deterministic pipeline in the recommendation flow
**Decision:** the orchestrator's `pipeline_market`, `pipeline_sentiment`, and `pipeline_decision` stages call the tools directly in Python, without going through the LLM's ReAct flow. The LLM is used only in the final stage to narrate the result.
**Rationale:** guaranteed reliability on the primary path—it eliminates the risk of the model skipping a stage or calling the wrong tool.
**Accepted trade-off:** the recommendation flow is less "agentic" in the strict
sense, offset by genuine dynamic routing for market, sentiment, diagnostic, and
contextual questions.

## Primary LLM
**Current decision:** `Qwen/Qwen3-235B-A22B-Instruct-2507` via the DeepInfra API.
**Integration:** `langchain_openai.ChatOpenAI` with
`base_url="https://api.deepinfra.com/v1/openai"`, `temperature=0.1`, and the
`DEEPINFRA_API_KEY` loaded from the environment.
**Historical note:** the initial plan evaluated Qwen 2.5 7B and named Llama 3.1
8B as a possible fallback. Those names describe the earlier planning decision,
not the model configured by the current source.

## Sentiment model
**Decision:** FinBERT-PT-BR via HuggingFace transformers, inference only.
**Rationale:** a model specialized in Portuguese financial sentiment. Do not train it—use the pretrained model.
**Note:** do not use LeIA/VADER in parallel. Use a single sentiment model on the critical path.

## State persistence
**Decision:** local CSV persistence for recommendation history.
**Rationale:** `data/recommendations.csv` is simple and human-readable, and its
schema can be consumed by later analysis. `save_recommendation` creates the
parent directory and appends rows; `load_recommendations` reads them for the
Gradio sidebar.
**Current limitation:** conversation state is held in the Gradio session while
the interface is running. No `data/sessions.json` persistence is implemented.

## Recommendation output format
**Decision:** structured JSON internally, converted to natural-language text for display.
**Rationale:** JSON ensures consistency for persistence and backtesting. Natural-language text improves the demo experience.
**Required JSON fields:** ticker, date, recommendation, confidence, rsi, macd_signal, sentiment_score, sentiment_label, top_headlines, reasoning.
**Recommendation enum:** always validate against `Recommendation(COMPRAR, VENDER, AGUARDAR)` before persisting.
**Note:** a plain `model_dump()` returns the enum member (`<Recommendation.COMPRAR: 'COMPRAR'>`) instead of the string `"COMPRAR"`, corrupting the CSV output. Always use `model_dump(mode="json")` on `RecommendationOutput`.

## Backtest without look-ahead bias
**Decision:** the backtest (`run_backtest`) does not call the LLM or FinBERT—it uses only technical indicators through a pure function (`apply_decision_rules`) and fixed neutral sentiment (`sentiment_score=0.5`) for every date.
**Rationale:** a natural-language narrative adds no value in a historical loop covering hundreds of days; real news sentiment is not available for past dates through RSS (it exists only for the present).
**Update (Stage 6.5):** fixed neutral sentiment remains the behavior with `use_gdelt=False`; by default (`use_gdelt=True`), the backtest now uses real historical sentiment through GDELT/BigQuery—see the "Historical sentiment through GDELT/BigQuery" decision below.
**Note (look-ahead bias):** `end=` in `yf.download` is **exclusive** (confirmed empirically and not clearly documented by yfinance)—`yf.download(ticker, end=date)` returns data only through the trading session **before** `date`, never including `date`. Therefore, `get_historical_features(ticker, date)` (`targets.py`) calculates the indicators using the closing price from the last trading session before `date`, never the closing price on `date` itself—a safeguard against look-ahead bias that is even more conservative than the minimum requirement (it never uses even the decision day's data). Meanwhile, `start=` is inclusive (also confirmed), so `get_forward_return`/`get_ibovespa_return` use `start=date`, ensuring that the future return is measured from the actual price on `date`, the decision day.

## Historical sentiment through GDELT/BigQuery (Stage 6.5)
**Decision:** completely replace the REST API-based GDELT client (`gdeltdoc`) with Google BigQuery as the canonical source of historical sentiment for the backtest. This is the definitive implementation, not a future improvement.
**Rationale:** the GDELT REST API had severe, officially undocumented rate limiting—~30min to collect 3 weeks of data for 4 tickers—which would make the complete 90-day backtest take several hours. BigQuery accesses the same public GDELT dataset without this rate limit.
**Implementation:** `google-cloud-bigquery` queries `gdelt-bq.gdeltv2.gkg_partitioned` (the same GDELT GKG, partitioned by day through `_PARTITIONTIME`, which enables partition pruning and reduces bytes scanned from ~21TB to ~0.3-0.5GB per query). Filtering uses `AllNames LIKE` with the keywords from `TICKER_KEYWORDS` through `UNNEST`—without the size/special-character restrictions imposed by the REST API (`_safe_gdelt_keywords` is no longer necessary, and the complete keyword list is used). Tone is extracted from the first field of `V2Tone` (`SPLIT(...)[OFFSET(0)]`), aggregated with `AVG` in BigQuery itself, and normalized with `(tone+10)/20`. GCP Project ID: `entrega-multi-agents` (authentication through `gcloud` Application Default Credentials, with no service key in the repository).
**Accepted trade-off:** `fetch_gdelt_sentiment` still runs one sequential BigQuery query per ticker/day combination—for the complete backtest (90 days × 4 tickers = 243 calls), this takes ~25min. Acceptable for the current volume (minutes, not the hours required by the REST API), but it does not scale indefinitely. A future improvement is documented in `docs/progress.md`: a single batch query (`GROUP BY ticker, date`) covering the entire period, along with bulk downloading in `yfinance` (the same sequential-call pattern used in `get_historical_features`/`get_forward_return`, `targets.py`).

## Backtest notebook working directory—separate notebooks/data/ and data/
**Observation:** `notebooks/04_backtest_and_evaluation.ipynb` runs with its working directory set to the notebook's own directory (`notebooks/`), not the repository root—the default behavior of `jupyter nbconvert --execute` and also of Jupyter kernels configured with `notebookFileRoot` relative to the file. Consequently, the relative paths used in the cells (for example, `Path("data/backtest_results.csv")`) resolve to `notebooks/data/...`, not to `data/...` at the root. This is why `notebooks/data/` (and `notebooks/reports/figures/`) exists separately from the `data/` directory used by `scripts/` (which are executed from the repository root; for example, `scripts/run_backtest_gdelt.py` writes to `<raiz>/data/backtest_results_gdelt.csv`).
**Note:** the two directories are not the same—a `pd.read_csv("data/algo.csv")` call inside the notebook will never find a file saved in `<raiz>/data/`. To compare a result generated by a script (root) with what the notebook expects to read, the CSV must be copied to `notebooks/data/` before running the read cell. This explains why `data/backtest_results_gdelt.csv` (root, generated by `scripts/run_backtest_gdelt.py`) and `notebooks/data/backtest_results_gdelt.csv` (copy, read by the comparison cell) coexist in the repository.

## Technical indicator library
**Decision:** pandas-ta.
**Rationale:** TA-Lib has a native dependency that causes installation problems on Windows. pandas-ta is pure Python.

## Tests
**Decision:** pytest coverage focused on critical context routing,
recommendation persistence and validation, sentiment behavior, and technical
features.
**Static inventory:** 23 `test_*` functions are currently defined across the
tracked test modules. This is a source count, not a claim that the tests were
executed during the documentation update.

## MVP ticker
**Decision:** PETR4.
**Rationale:** high liquidity, a high volume of Portuguese-language news, and exposure to multiple contextual areas (energy, politics, geopolitics).

## What is not on the critical path
- Azure, social media—portfolio extensions, not MVP dependencies
- Context Router and the Asset Context Map were implemented as post-delivery
  bonus work; broader contextual-source coverage remains optional
- Supervised model using historical features—bonus work, implement after Stage 6
- Deep Learning (LSTM, Transformer)—leave for a future project
