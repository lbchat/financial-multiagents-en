# Translation Project Ledger

This ledger records the translation policy, completed work, protected content,
remaining work, and validation baseline for the English repository. Git state
remains authoritative.

## 1. Repository identity

- Original Portuguese repository: `lbchat/entrega-multiagents`
- English repository: `lbchat/financial-multiagents-en`
- Translation branch: `translate-to-english`
- Recorded translation HEAD: `06b0bbb19c0266d7809e7b98a9c744c9a8a48da8`
- Baseline commit: `4cf6d3a4bdb2234baec30746809d55467a07d641`
- Baseline tag: `pre-translation-baseline`
- The original Portuguese repository must remain untouched.
- `upstream` is fetch-only, and its push URL is disabled.

## 2. Approved language policy

- Engineering documentation, comments, ordinary developer-facing docstrings,
  and notebook Markdown use English.
- Application functionality remains Brazilian Portuguese only.
- Questions, answers, prompts, UI text, runtime messages, errors, warnings,
  recommendation reasoning, and persisted reasoning remain PT-BR.
- LangChain/LLM-visible `@tool` docstrings remain PT-BR.
- Uncertain runtime-visible docstrings remain PT-BR pending review.
- FinBERT-PT-BR inputs, mappings, Portuguese keywords, aliases, and contextual
  keyword maps remain unchanged.
- Preserve `COMPRAR`, `VENDER`, `AGUARDAR`, `POSITIVO`, `NEGATIVO`, and
  `NEUTRO`.
- Preserve identifiers, routes, schemas, keys, CSV fields, paths, filenames,
  model names, and historical artifacts.
- CSVs, PNGs, notebook outputs, execution counts, and notebook metadata remain
  unchanged by default.

## 3. Safety rules

- Never translate via global search-and-replace.
- Change only explicitly inventoried comments and docstrings per batch.
- Prompts and runtime strings must be hashed or compared before and after when
  they share a file with translated annotations.
- Python batches require AST parsing and normalized AST comparison.
- Non-docstring string constants must remain byte-identical.
- Notebook edits must preserve outputs, images, execution counts, metadata,
  cell order, and cell types.
- No tests, notebooks, models, APIs, or application modules are executed merely
  for translation.
- Each batch has one small, reviewable commit.
- Nothing is pushed until the final audit passes.

## 4. Completed commits

- [x] `1ae1607` — `docs: translate README and architecture overview`
- [x] `adcd000` — `docs: translate architectural decisions and project progress`
- [x] `6f1ebe5` — `docs: translate historical execution plan`
- [x] `356652a` — `docs: translate core development instructions`
- [x] `75a4f9f` — `docs: translate development patterns guide`
- [x] `31ebef7` — `docs: define Portuguese runtime language policy`
- [x] `4afbfe1` — `docs: translate data-layer developer annotations`
- [x] `c940c85` — `docs: translate feature and context annotations`
- [x] `8ba3c49` — `docs: translate backtesting and storage annotations`
- [x] `6edef5c` — `docs: translate agent builder annotations`
- [x] `233b42f` — `docs: translate orchestrator developer annotations`
- [x] `030b155` — `docs: translate Gradio developer docstrings`
- [x] `6e4b5e2` — `docs: translate non-runtime tool-module annotations`
- [x] `5d92f56` — `docs: translate script developer annotations`
- [x] `d85f05e` — `docs: translate context output and recommendation test docstrings`
- [x] `967139e` — `docs: translate sentiment and technical test docstrings`
- [x] `09927b5` — `docs: translate notebook code-cell docstrings`
- [x] `06b0bbb` — `docs: translate notebook Markdown documentation`

## 5. Protected inventory

- Five protected LangChain `@tool` docstrings:
  - `scripts/test_llm.py::get_ticker_info`
  - `tools/context_tools.py::analyze_context`
  - `tools/decision_tools.py::generate_recommendation`
  - `tools/market_tools.py::get_market_features`
  - `tools/news_tools.py::get_sentiment_features`
- Protected `# AGUARDAR` comment in `backtesting/metrics.py`
- All explicit agent and router prompts
- All Gradio-visible strings
- Portuguese financial-news keywords and aliases
- `context_map.yaml`
- FinBERT mappings
- Historical CSV, PNG, and notebook-output content

## 6. Remaining work

- [x] Phase 2B-7 — safe tool-module annotations
- [x] Phase 2B-8 — script annotations, excluding protected `test_llm.py` tool
  docstring
- [x] Phase 2B-9 — context, output, and recommendation test docstrings
- [x] Phase 2B-10 — sentiment and technical test docstrings
- [x] Phase 2B-11 — notebook code-cell docstrings
- [x] Translate notebook Markdown cells while preserving all outputs and
  metadata
- [ ] Repository-wide Portuguese occurrence audit
- [ ] Documentation-accuracy corrections in separate commits
- [ ] Final diff, AST, notebook, artifact, and contract audit
- [ ] Push translation branch
- [ ] Open and review pull request
- [ ] Merge into the English repository's `main`

Runtime UI and prompt translation is intentionally excluded.

## 7. Recorded validation baseline

- Tracked Python files: 45
- Python AST parses: 45/45
- Notebooks: 5
- Notebook cells: 44
- Code cells: 26
- Markdown cells: 18
- Saved output objects: 72
- Embedded images: 4

Notebook-output and image hashes were captured during Phase 2A and must be
rechecked before notebook commits and during the final audit.

## 8. Ledger maintenance rule

- Every future Codex prompt must begin by reading this ledger.
- After each successful batch, update only:
  - current HEAD;
  - completed-commit list;
  - remaining-work checklist;
  - newly discovered protected items or decisions.
- Ledger updates must be included in a separate small commit or in the final
  bookkeeping commit, never mixed silently into a translation batch.
- Git state remains the authority if the ledger and repository disagree.
- Any disagreement requires stopping before edits.
