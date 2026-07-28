# Project Status

> Update this section after completing each stage.

## Stages

- [x] **Stage 0**—Foundation: repository, environment, folder structure, .env.example, initial README
- [x] **Stage 1**—Market pipeline: yfinance + pandas-ta working for PETR4, validated in a notebook
- [x] **Stage 2**—Sentiment pipeline: feedparser + FinBERT-PT-BR working for PETR4, validated in a notebook
- [x] **Stage 3**—MVP agent: 3 tools + ReAct + complete recommendation for PETR4
- [x] **Stage 4**—Expansion: agent working for VALE3, BBAS3, and ITUB4
- [x] **Stage 5**—Gradio interface: navigable conversational demo
- [x] **Stage 6**—Backtest: historical simulation + comparison against buy-and-hold and the Ibovespa
- [x] **Stage 7**—Delivery: final README, architecture diagram (`docs/architecture.md`), end-to-end demo notebook (`05_demo.ipynb`), known limitations, and documented next steps

## Post-delivery improvements

> Project academically completed (Stages 0-7). Post-delivery development begins here.

### Completed
- [x] Investigative diagnostic agent
- [x] MarketAgent prompt correction for explicit comparisons
- [x] Context Router Agent with Asset Context Map
- [x] Contextual-sphere analysis using ticker-specific keyword maps and
  per-sphere sentiment aggregation

**Current static test inventory:** 23 `test_*` functions are defined in the
tracked test modules. This is a source inventory, not a current test-execution
result.

### In progress
- [ ] *(no items currently in progress)*

### Backlog
- [ ] Batch queries in the backtest (BigQuery GROUP BY + yfinance bulk)
- [ ] CVM integration—historical material disclosures by ticker
- [ ] BCB Focus Report integration—weekly macroeconomic expectations
- [ ] Automated alerts through Telegram + GitHub Actions
- [ ] Persistence in Azure Blob Storage
- [ ] Portfolio comparison by risk profile

## Original bonus-work plan, reconciled with current status

> This preserves the original priority order while showing which proposals
> were implemented during post-delivery development.

- [x] Asset Context Map + Context Router Agent
- [ ] In-depth backtest (walk-forward, complete financial metrics)
- [x] Analysis by contextual areas through the implemented Asset Context Map,
  keyword routing, and per-sphere sentiment
- [ ] Long-term agent memory
- [ ] Supervised model using historical features
- [ ] Automated alerts through Telegram
- [ ] Persistence in Azure Blob Storage

### Ideas for highlighting genuine agency (ReAct) in the portfolio

**Suggestion 1—Free-form question agents (implemented, still useful to highlight)**

Dynamic routing through `market_node`, `sentiment_node`, `diagnostic_node`, and
`context_node` uses ReAct agents for question-specific work. It requires no new
implementation to demonstrate this behavior; examples in the notebook and
Gradio can make the routing and tool use visible to the evaluator.

**Suggestion 2—Investigative diagnostic agent (historical proposal, now implemented)**

The proposal was an open-question mode where the user could ask questions such
as "Por que VALE3 está caindo?" ("Why is the stock falling?") or "O que explica
o comportamento de PETR4 hoje?" ("What explains the stock's behavior today?").
It was subsequently implemented as `DiagnosticAgent` and `diagnostic_node`,
with access to the market, sentiment, and recommendation tools.

**Suggestion 4—Context Router Agent (historical proposal, now implemented)**

The proposal called for ticker-specific contextual dimensions such as
political, environmental, regulatory, and macroeconomic factors. It was
subsequently implemented through `context_map.yaml`, contextual keyword
routing, `analyze_context`, `ContextRouterAgent`, and `context_node`.

## Notes and blockers

<!-- Record implementation blockers, open questions, or decisions here -->

- AVG Antivirus performs HTTPS inspection (MITM) and blocks Python SSL calls with `CERTIFICATE_VERIFY_FAILED`. Fixed by installing `pip-system-certs` in `.venv` (which makes Python trust the Windows certificate store). If the virtual environment is reinstalled from scratch, repeat this step.
- `yfinance` uses `curl_cffi` under the hood, which has its own certificate bundle and is not covered by `pip-system-certs`. Fixed by exporting the AVG root certificate (`Cert:\LocalMachine\Root`, subject "AVG Web/Mail Shield Root") and appending it to the `certifi` `cacert.pem` file inside `.venv`. If the virtual environment is reinstalled from scratch, repeat this step as well.
- The actual `id2label` for `lucas-leme/FinBERT-PT-BR` is `{0: POSITIVE, 1: NEGATIVE, 2: NEUTRAL}`, not `{0: negativo, 1: neutro, 2: positivo}` as initially assumed in `sentiment.py`. Fixed the order of the `labels` list. A regression test (`test_classify_sentiment_correct_polarity`) would catch this bug if it reappeared.
- A plain `RecommendationOutput.model_dump()` returns the enum member (`<Recommendation.COMPRAR: 'COMPRAR'>`) instead of the string `"COMPRAR"`, which would corrupt the CSV output. Always use `model_dump(mode="json")` in `decision_tools.py`. Regression test: `test_recommendation_output_serializes_enum_as_plain_string`.
- `create_react_agent` in the installed version of LangGraph (1.2.6) no longer accepts the `state_modifier` parameter (used in older examples)—the correct name is now `prompt`. This affects `market_agent.py`, `sentiment_agent.py`, and `decision_agent.py`.
- Circular import between `agents/decision_agent.py` (which needs `generate_recommendation`) and `tools/decision_tools.py` (which needs `Recommendation`/`RecommendationOutput`). Resolved with a late import (inside `build_decision_agent()`).
- The fixed recommendation pipeline (`pipeline_market` → `pipeline_sentiment` → `pipeline_decision`) cannot chain 3 ReAct agents while passing along the accumulated conversation—the LLM at each stage, seeing a conversation that already "looked answered" by the previous stage, frequently decided not to call its tool (or refused, or returned nothing), and the `DecisionAgent` would even hallucinate a free-text recommendation without ever calling `generate_recommendation`, so the CSV was never written. Resolved by calling the tools directly in Python in these 3 stages (deterministically), with a `PipelineState` carrying `ticker`/`market_features`/`sentiment_features` between them; the LLM (`DecisionAgent`) is used only at the end to narrate the already calculated result. The dynamic routing nodes (`market_node`, `sentiment_node`) continue using the ReAct agents normally—they work well because they receive only the original question, with no accumulated history from other stages.
- `pandas-ta` 0.4.71b0 (installed version) generates Bollinger Bands column names with a duplicated suffix: `BBU_20_2.0_2.0`/`BBL_20_2.0_2.0`, not `BBU_20_2.0`/`BBL_20_2.0` as in older versions. Fixed in `technical.py`.
- Unicode characters `✓`/`✗` in `print()` break the PowerShell console (codepage cp1252, not UTF-8) with `UnicodeEncodeError`, interrupting the script midway through execution. Replaced with the ASCII strings `OK:`/`FALHOU:` in `scripts/test_expansion.py`.
- `gr.Chatbot` in the installed version of Gradio (6.19.0) no longer accepts the `type="messages"` parameter (it is now the only format, with no option). Removed from the constructor. Message values continue to use `{"role": ..., "content": ...}`.
- To validate the Gradio interface with Playwright (a real browser), the Playwright browser downloader uses Node.js internally and encounters the same AVG SSL problem, but through a mechanism different from Python (`certifi`) and `yfinance` (`curl_cffi`). Fixed by setting `NODE_OPTIONS=--use-system-ca` before running `playwright install chromium`, which makes Node trust the Windows certificate store.
- The `end=` parameter of `yf.download` is **exclusive** (confirmed empirically): `yf.download(ticker, end="2026-03-03")` returns data only through 2026-03-02, without including day 03. In `targets.py`, `get_historical_features(ticker, date)` therefore calculates the indicators using the closing price from the last trading session **before** `date`, not the closing price on `date` itself—a safeguard against look-ahead bias that is even more conservative (it never uses even the decision day's data). Meanwhile, `start=` is inclusive, also confirmed, so `get_forward_return`/`get_ibovespa_return` use `start=date` to ensure that the price on `date` (the decision day) is the starting point for the measured future return.
- The "business day" check based only on `dayofweek` (which excludes weekends) does not detect B3 holidays (for example, Carnival—16 and 17/02/2026 were market holidays, but trading took place normally on Ash Wednesday, 18/02). Without an additional check, `yf.download(start=date, ...)` silently "slides" to the next available trading session, causing consecutive holiday dates to return **identical, duplicated** values (the same price/indicators) and artificially inflating the backtest sample with non-independent rows. Fixed in `targets.py`: `_is_trading_day()` checks whether `date` had an actual trading session before `get_historical_features` proceeds; `_compute_forward_return()` verifies that the first returned row corresponds exactly to `date` before calculating the return. Both now correctly return `None` for holidays.
- **Historical sentiment limitation (Stage 6, overcome in Stage 6.5):** the backtest (`run_backtest`, `strategy.py`) used a fixed `sentiment_score=0.5` (neutral) for every date because news sentiment through RSS exists only for the present—there was no way to obtain historical news for past dates from the current feeds. This meant that the backtest results primarily evaluated the quality of the technical indicators (RSI, MACD) as decision signals, not the complete strategy. Also documented in a Markdown cell in the `04_backtest_and_evaluation.ipynb` notebook. **Overcome in Stage 6.5:** by default (`use_gdelt=True`), the backtest now uses real historical sentiment through GDELT/BigQuery; `sentiment_score=0.5` continues to be used only in `use_gdelt=False` mode (comparison) and as the `fetch_gdelt_sentiment` fallback when no data is available for the period.
- **GDELT through REST API (Stage 6.5, discontinued—historical record below):** `article_search` from the `gdeltdoc` library **does not return a `tone` column** (unlike what the documentation/examples suggest)—tone is available only through the dedicated `timeline_search("timelinetone", filters)` mode, which returns an "Average Tone" series at 15-minute intervals. The client made 2 calls: `article_search` for `news_count` and `timeline_search` for the average tone.
- **GDELT—query size/syntax limit (historical, REST API):** passing the complete `TICKER_KEYWORDS` list (up to ~30 terms) exceeded the GDELT query size limit ("query was too short or too long"), and terms with special characters such as a hyphen or `+` were rejected by the API (for example, `"pré-sal"`, `"OPEP+"`). At the time, this was worked around with `_safe_gdelt_keywords()`: only the first `MAX_GDELT_KEYWORDS=5` terms for each ticker were used, discarding any term containing `-` or `+`.
- **GDELT—aggressive rate limiting (historical, REST API):** experiments confirmed that the API's informal rate limit is far more restrictive than it initially appears—even pauses of 8-15s between consecutive calls during manual tests still occasionally resulted in `RateLimitError`. Because `fetch_gdelt_sentiment` never raises an exception (by contract), a rate-limited call silently returned the neutral fallback—indistinguishable from "no real coverage" without inspecting the logs. This was the main reason for the migration to BigQuery described below.
- **GDELT—migration from REST API to BigQuery (Stage 6.5, canonical decision):** the 3 notes above describe problems with the `gdeltdoc`/REST API implementation, now completely replaced by Google BigQuery (`google-cloud-bigquery`) as the definitive source of historical sentiment—this is not a future improvement; it is the implementation in production in `gdelt_client.py`. The full rationale, implementation details, and accepted trade-offs are in `docs/decisions.md` ("Historical sentiment through GDELT/BigQuery"). GCP Project ID: `entrega-multi-agents`. The 3 notes above remain only as a historical record of what was investigated in the previous implementation.
- **Lesson learned—an orphaned process overwrote an already validated result (Stage 6.5):** after `data/backtest_results_gdelt.csv` had been validated with 244 rows and 0% neutral fallback, the same file appeared hours later with only 60 rows and 78% neutral fallback—even though nothing in the current session had run the script again. Cause: a Python process from a previous session, still running the old implementation (`gdeltdoc`/REST API, 21-day window, aggressive fallback due to rate limiting), remained in the background after `gdelt_client.py` and `run_backtest_gdelt.py` were rewritten. The process already had the old module loaded in memory, so the source-file edits did not affect it, and it finished only much later, overwriting the CSV after validation had been confirmed as correct. **Lesson:** an output file is trustworthy only at the moment it is read; if a long-running script may still be running from a previous session, check active processes before proceeding (`Get-CimInstance Win32_Process -Filter "Name='python.exe'"` in PowerShell)—and when rewriting a module, remember that running processes continue to use the old version in memory until they are restarted. Resolved by confirming that no processes were still running and rerunning the current script to regenerate the correct CSV.
- **Valor Econômico RSS feed replaced (before Stage 7):** `https://valor.globo.com/rss/home/` (in `RSS_FEEDS`, `news_data.py`) returned 0 items—`feedparser` did not raise an error and simply returned an empty result (the actual response was HTTP 400 and HTML, not XML). The 3 alternatives provided by Valor itself (`/rss/`, `/financas/rss`, `/empresas/rss`) were tested and were also broken (404, or redirecting to the generic Globo.com error page). Replaced with `https://br.investing.com/rss/news_285.rss`: the same domain suggested as a fallback (`br.investing.com`), but using a news category specific to the Brazilian market (Selic, the U.S. dollar, B3 tickers) instead of the generic `/rss/news.rss` feed (which returns insider-trading news about U.S. companies, with no relevance to the tracked tickers). RSS is volatile by nature—the pipeline already handles the absence of relevant news at query time with the neutral fallback (`sentiment_score=0.5`, `news_count=0`), so the replacement does not need to guarantee an immediate match for every query, only increase the chance of real coverage over time (previously, the Valor feed never contributed any items to any query).
- **Headlines now show the summary excerpt that explains the match (before Stage 7):** `fetch_news` matches keywords against the combined title+summary (`TICKER_KEYWORDS`, `news_data.py`), but `top_headlines` (`aggregate_sentiment`, `sentiment.py`) displayed only the title. As a result, the headline shown to the user sometimes appeared unrelated to the ticker when the matching term was actually in the summary. Fixed with `_format_headline()`: when the summary exists and differs from the title, it appends an excerpt of up to `HEADLINE_SUMMARY_EXCERPT_LENGTH=100` characters using the format `"Título — trecho..."`. The CSV field contract does not change (it remains `list[str]`); only the content of each string changes.
- **Investigative diagnostic agent (post-delivery):** new `diagnostic_node` in `orchestrator.py`, with a genuine ReAct `DiagnosticAgent` (`agents/diagnostic_agent.py`) that has access to the system's 3 tools (`get_market_features`, `get_sentiment_features`, `generate_recommendation`) and is selected when the question is open-ended/investigative. The router (`ROUTER_PROMPT`) was expanded from 3 to 4 categories. `generate_recommendation` is available as an additional data source for the investigation, but the prompt explicitly prohibits issuing a formal recommendation as the conclusion—the agent's role is to explain, not recommend. Validated with the Portuguese input "Por que VALE3 está caindo nos últimos dias?" ("Why has the stock been falling in recent days?"): the agent called `get_market_features` and `get_sentiment_features` in sequence before concluding, synthesizing both into a single analysis—genuine multi-tool ReAct, not a fixed pipeline. **Historical validation recorded at that stage:** the 3 existing routes (`market_node`, `sentiment_node`, `pipeline_market`) continued to work without regression (20/20 tests).
- **Context Router Agent with Asset Context Map (post-delivery):** new `context/` module—`context_map.yaml` (4 tickers, thematic areas with specific keywords: energy/politics_regulation/geopolitics/labor_social for PETR4, mining_commodities/china_demand/environmental/macro for VALE3, etc.), `router.py` (`get_context_keywords`, `route_context_search`—classifies already collected news by area through keyword matching; one article can fall into multiple areas). The `analyze_context` tool (`tools/context_tools.py`) retrieves news through `fetch_news`, routes it by area, and reuses `aggregate_sentiment` (already tested, already using FinBERT) for sentiment in each area—without duplicating aggregation logic. `ContextRouterAgent` (`agents/context_router_agent.py`) narrates the results by area and never issues a formal recommendation. The router was expanded from 4 to 5 categories (new: `"context"`). Added `pyyaml` as an explicit dependency in `pyproject.toml` (it was already included transitively and is now declared). 3 new tests were added in `test_context_router.py`. **Historical validation recorded at implementation time:** pytest 23/23. **Functional validation confirmed the real success case**: a question about ITUB4 ("Quais fatores externos estão afetando ITUB4?", meaning "What external factors are affecting the stock?") explicitly narrated the `macro_rates` area with NEGATIVO sentiment and the real article that motivated it (JCP/Sanepar). It also confirmed the expected behavior when there is no coverage: VALE3, PETR4, and, on a second call minutes later, BBAS3 returned no active areas—the same RSS volatility already documented (the crop article that classified BBAS3 under `credit_agro` during Task 3 validation was no longer at the top of the feed minutes later). The 4 existing routes continued to work without regression in that historical validation.
- **Fix—ContextRouterAgent invented generic areas when there was no coverage (post-delivery):** the original `build_context_router_agent()` prompt mentioned only generic categories (`"energia, política, geopolítica, ambiental"`, meaning "energy, politics, geopolitics, environmental"), with no connection to the actual areas registered by ticker in `context_map.yaml`. Consequently, when no news was available, the LLM hallucinated plausible-but-incorrect names instead of citing the configured areas. Fixed: the function now receives `ticker` as a parameter, reads `get_context_keywords(ticker)`, and injects the actual areas into the prompt before building the agent. The agent is therefore now built per request in `context_node` (`orchestrator.py`), rather than only once when the graph is initialized like the other agents. In addition, `analyze_context` (`context_tools.py`) now returns `monitored_spheres` (the list of areas registered for the ticker) whenever `spheres_analyzed` is empty, giving the agent a reliable source to cite even without coverage. Validated with `ask("Como está o contexto político para BBAS3?")`: the agent correctly cited the ticker's 3 actual areas (fiscal_policy, banking, credit_agro), including the one with no coverage at that time—no invented generic names. **Historical validation recorded for that fix:** pytest 23/23 with no regression.

## Improvements before Stage 7

- **Backtest performance (Stage 6.5, after the BigQuery migration):** `fetch_gdelt_sentiment` (`gdelt_client.py`) runs one BigQuery query per ticker/day combination—243 calls for 90 days × 4 tickers, ~25min of execution. `get_historical_features`/`get_forward_return` (`targets.py`) follow the same pattern with `yf.download`, one call per day/ticker. Both could become batch calls: a single BigQuery query with `GROUP BY ticker, date` covering the entire period at once, and a single `yf.download` per ticker retrieving the complete window and filtering locally—eliminating most network round trips. Not implemented at this stage because the current time (~25min) is already within the acceptable range ("minutes, not hours"); worth revisiting if the backtest grows (more tickers, a longer period, or recurring execution).
- **MarketAgent prompt corrected for explicit comparisons (post-delivery):** a comparative question requesting an explanation/summary (for example, the Portuguese input "Compare os indicadores de ITUB4 e BBAS3, fornecendo não só os indicadores mas também uma breve explicação resumindo o que for mais relevante", meaning "Compare the indicators for the two stocks, providing not only the indicators but also a brief explanation summarizing what is most relevant") was routed to `market_node`, which correctly called `get_market_features` for both tickers, but the `MarketAgent` prompt explicitly prohibited any interpretation/summary. It therefore collected the data and returned the Portuguese message `"Dados coletados. Outra etapa do sistema será responsável pela análise comparativa e resumo."` (meaning "Data collected. Another stage of the system will be responsible for the comparative analysis and summary.") instead of answering the comparative/explanatory part of the request. **Fixed** in `market_agent.py`: a paragraph was added to the prompt explicitly authorizing structured comparison between tickers (while retaining the prohibition on formal recommendations). Validated with the Portuguese input "Compare os indicadores técnicos de ITUB4 e BBAS3, destacando o que for mais relevante" ("Compare the technical indicators for the two stocks, highlighting what is most relevant")—the response now compares RSI, MACD, moving averages, and Bollinger Bands for both tickers using real data, without a formal recommendation.
