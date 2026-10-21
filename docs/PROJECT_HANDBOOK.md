# AI Marketing Analytics Platform
## Engineering Handbook v4.0

---

## 1. Project Overview

This is a modular, production-quality AI Marketing Analytics Platform designed to ingest raw marketing campaign CSVs, match fields dynamically, validate schema & structural rules, clean dirty rows, perform advanced KPIs & segmented cohort calculations, and present data-rich visual dashboards alongside:

- An **AI Consultant** powered by Google Gemini that answers natural-language questions grounded in the campaign analytics context.
- A **RAG-based Ad Copy Advisor** powered by a ChromaDB vector store and the Gemini Embedding API, which retrieves domain knowledge (mobile feed rules, direct-response frameworks, readability diagnostics) to give copywriting and creative guidance.

---

## 2. Actual Modular Architecture (Current State)

```
market_analyzer/
├── assets/
│   ├── knowledge_base/              # RAG knowledge base markdown documents
│   │   ├── mobile_feed_rules.md
│   │   ├── direct_response_frameworks.md
│   │   └── readability_diagnostics.md
│   ├── vector_store/                # Persistent ChromaDB storage (auto-created at runtime)
│   └── sample_data/                 # Sample datasets
├── config/
│   ├── __init__.py
│   └── settings.py                  # All constants: column sets, aliases, dropdown options
├── Data/                            # Note: actual folder is capitalised "Data/"
│   ├── loader.py                    # File ingestion (CSV, XLSX, PDF)
│   └── filter.py                    # User-driven date / campaign filtering
├── mapping/
│   ├── __init__.py
│   └── column_mapper.py             # Alias-based column header auto-mapping
├── cleaning/
│   ├── __init__.py
│   └── data_cleaner.py              # Type coercion, symbol stripping, deduplication
├── validation/
│   ├── __init__.py
│   ├── validator.py                 # Orchestrator: runs all sub-validators in sequence
│   ├── schema_validator.py          # Mandatory column presence checks
│   ├── structural_validator.py      # Row count, empty column structural checks
│   ├── duplicate_validator.py       # Duplicate mapping collision checks (pre-analytics)
│   ├── missing_value_validator.py   # Missing value % thresholds per column
│   ├── duplicate_row_validator.py   # Identical row detection
│   ├── business_logic_validator.py  # Spend vs budget, CTR sanity, etc.
│   └── derived_metric_validator.py  # Uploaded vs calculated metric discrepancy detection
├── analytics/
│   ├── __init__.py
│   ├── analytics_engine.py          # Master orchestrator for the full analytics pipeline
│   ├── utils.py                     # Shared math helpers (safe_divide, formatters)
│   ├── kpi.py                       # Account-level aggregate KPIs
│   ├── campaign_analysis.py         # Per-campaign performance segmentation
│   ├── audience_analysis.py         # Age group & gender breakdowns
│   ├── device_analysis.py           # Device-type performance breakdowns
│   ├── objective_analysis.py        # Campaign objective breakdowns
│   ├── time_analysis.py             # Date-based trend series
│   ├── funnel_analysis.py           # Impressions → Clicks → ATC → Purchases funnel
│   ├── anomaly_detection.py         # Multi-severity anomaly detection rules engine
│   ├── qualitative_analysis.py      # Ad copy readability & text metrics engine
│   └── graph_data.py                # Aggregated chart datasets for UI consumption
├── insights/
│   ├── __init__.py
│   ├── insight_engine.py            # Qualitative "what happened / why it matters" facts
│   ├── recommendation_engine.py     # Deterministic tiered action recommendations
│   └── summary_builder.py           # AI context payload assembler
├── ai/
│   ├── __init__.py
│   ├── ai_engine.py                 # Gemini API integration for AI Consultant Q&A
│   ├── chunker.py                   # Markdown knowledge base → heading-keyed chunks
│   ├── embedder.py                  # Chunk & query embedding via Gemini Embedding API
│   ├── vector_store.py              # ChromaDB ingestion: chunks → embeddings → store
│   ├── top_k.py                     # Similarity search: query embedding → top-k docs
│   ├── prompt_generator.py          # RAG prompt builder from top-k results + user query
│   └── llm_response.py              # (Stub) Future LLM response handler for RAG pipeline
├── visualization/
│   ├── __init__.py
│   ├── charts.py                    # Plotly chart factory functions (Bar, Line, Pie, Funnel, Scatter)
│   └── ui_components.py             # CSS loader, header banner, metric card wrappers
├── docs/
│   ├── PROJECT_HANDBOOK.md
│   └── ARCHITECTURE_DECISIONS.md
├── app.py                           # Streamlit Orchestrator UI (Executive Controller)
├── .gitignore
├── .env.example
├── README.txt
└── requirements.txt
```

---

## 3. Package Responsibilities

### Config (`config/`)
- Single source of truth for all column definitions: `MANDATORY_COLUMNS`, `OPTIONAL_COLUMNS`, `DERIVED_COLUMNS`, `QUALITATIVE` variants.
- `COLUMN_ALIASES`: the full alias dictionary used by the auto-mapper. Also includes ad copy columns (`primary_text`, `headline`, `ad_description`, etc.).
- `MAPPING_DROPDOWN_OPTIONS` and `QUALITATIVE_MAPPING_DROPDOWN_OPTIONS`: enumerated lists that power the UI column-mapping dropdowns.

### Data Handling (`Data/`)
- `loader.py`: Ingests CSV, XLSX, and PDF file objects uploaded through the Streamlit UI.
- `filter.py`: Applies user-selected date ranges and campaign filters to the cleaned DataFrame without mutating the original.

### Mapping (`mapping/`)
- `column_mapper.py`: Normalises raw headers (lowercase, strip, underscore) and matches each against `COLUMN_ALIASES` to produce a `Dict[str, Optional[str]]` prediction presented in the UI for user confirmation.

### Cleaning (`cleaning/`)
- `data_cleaner.py`: Operates on the user-confirmed, renamed DataFrame. Strips currency symbols and `%` signs, coerces integer count columns to `int64 → float64`, coerces currency/float columns to `float64`, normalises percentage columns, fills missing categoricals with `'Unknown'`, and drops fully duplicate rows. **Never validates business rules.**

### Validation (`validation/`)
- `validator.py`: Orchestrates all sub-validators in sequence and returns a single combined report. Duplicates and derived metric discrepancies are non-blocking warnings; schema, structural, missing-value, and business logic failures are blocking.
- `schema_validator.py`: Checks mandatory column presence.
- `structural_validator.py`: Checks row count and empty column thresholds.
- `duplicate_validator.py`: Detects duplicate canonical mappings before analytics (not row-level).
- `missing_value_validator.py`: Flags columns with excessive `NaN` ratios.
- `duplicate_row_validator.py`: Counts identical rows.
- `business_logic_validator.py`: Enforces invariants like spend ≤ budget, CTR in [0, 100], etc.
- `derived_metric_validator.py`: Compares uploaded CTR/CPC/CVR values vs system-calculated ones and reports discrepancies.

### Analytics (`analytics/`)
- `analytics_engine.py`: Master orchestrator. Computes derived metrics (CTR, CPC, CVR) from raw columns or normalises uploaded metrics. Calls all sub-calculators in order and passes the assembled `raw_analytics` dict to the insight and recommendation engines before returning the full combined report.
- `kpi.py`: Account-level totals and averages (spend, impressions, clicks, conversions, reach, CTR, CPC, CPM, conversion rate).
- `campaign_analysis.py`, `audience_analysis.py`, `device_analysis.py`, `objective_analysis.py`, `time_analysis.py`: Segmented aggregation modules producing per-entity performance tables with account-level KPI benchmarks for relative comparison.
- `funnel_analysis.py`: Computes Impressions → Clicks → Landing Page Views → Add to Cart → Purchases → Conversions funnel with inter-stage drop-off rates and bottleneck identification.
- `anomaly_detection.py`: Multi-severity rule engine that flags zero-spend-with-impressions, excessive CPC, budget overrun, high frequency, etc.
- `qualitative_analysis.py`: Processes `primary_text` and `headline` columns using `textstat` and `emoji` to produce per-row readability scores (Flesch-Kincaid grade, words per sentence, syllable density), mobile truncation flags, wall-of-text detection, offer/urgency visibility, and emoji density metrics.
- `graph_data.py`: Prepares all aggregated `pd.Series` and `pd.DataFrame` structures needed by the Plotly chart factories, guarding against missing column combinations.
- `utils.py`: Shared math helpers (`safe_divide`, formatting utilities) consumed across analytics sub-modules.

### Insights (`insights/`)
- `insight_engine.py`: Translates raw analytics dictionaries into categorised factual observations across 9 dimensions (KPIs, Campaigns, Audience, Devices, Objectives, Trends, Budget, Funnel, Overall Summary). **No math, no recommendations, no AI.**
- `recommendation_engine.py`: Applies deterministic rules to insights and anomalies to produce tiered recommendations (Critical → High → Medium → Low). Two interfaces: legacy `generate_recommendations` (used by `app.py`) and new `generate_action_recommendations` (called by `analytics_engine.py`).
- `summary_builder.py`: Assembles the AI context payload dictionary from KPIs, best performers, anomaly details, recommendations, and segment breakdowns for Gemini consumption.

### AI Engine (`ai/`)
The `ai/` package contains two separate AI subsystems:

#### 1. AI Consultant (Q&A grounded in analytics data)
- `ai_engine.py`: Sends the `build_ai_summary` payload plus the user's natural-language question to the `gemini-2.5-flash` model with a business-consultant system persona. Returns a 200–300-word executive response.

#### 2. RAG Ad Copy Advisor (knowledge retrieval pipeline)
The pipeline flows left to right:

```
knowledge_base/*.md
      ↓
  chunker.py          →  Dict[heading, {content, source}]
      ↓
  embedder.py         →  List[embedding]  (RETRIEVAL_DOCUMENT, gemini-embedding-2)
      ↓
  vector_store.py     →  ChromaDB PersistentClient  (assets/vector_store/)
                                     ↕
  user query string
      ↓
  embedder.embed_query()  →  List[float]  (RETRIEVAL_QUERY, gemini-embedding-2)
      ↓
  top_k.py            →  List[Dict]  (top-k nearest docs by inner product)
      ↓
  prompt_generator.py →  str  (system persona + retrieved docs + user query)
      ↓
  llm_response.py     →  (stub, not yet implemented)
```

- `chunker.py`: Reads the three knowledge base `.md` files and splits each on `##` headers using regex. Returns `Dict[heading, {"content": str, "source": filename}]`. Handles missing files, empty sections, and duplicate heading collisions with counter suffixes. Path resolved relative to `__file__`.
- `embedder.py`: `embed_document_chunks` iterates the chunk dict and calls `client.models.embed_content` with `task_type="RETRIEVAL_DOCUMENT"`. `embed_query` takes a raw query string and embeds it with `task_type="RETRIEVAL_QUERY"`. Both functions load the API key from `.env`, validate inputs, and wrap API calls in `try-except`.
- `vector_store.py`: `add_documents_to_vector_store` orchestrates chunk generation → embedding → ChromaDB ingestion. Uses `PersistentClient` with `hnsw:space=ip` (inner product). Path resolved relative to `__file__`.
- `top_k.py`: `top_k(query_embeddings, k)` connects to ChromaDB, queries the collection, validates the response structure and alignment, and returns a clean list of dicts `{id, content, metadata, distance}`. Path resolved relative to `__file__`.
- `prompt_generator.py`: `generate_prompt(user_query, top_k_results)` prepends the direct-response media buyer persona and appends retrieved document content and metadata, then appends the user query at the end.
- `llm_response.py`: Currently an empty stub. Intended to call Gemini with the assembled prompt and return the final creative copywriting response.

### Visualization (`visualization/`)
- `charts.py`: Stateless Plotly figure factories (`create_bar_chart`, `create_scatter_chart`, `create_line_chart`, `create_pie_chart`, `create_funnel_chart`) using a shared off-white executive light theme.
- `ui_components.py`: Loads `style.css` from `.streamlit/`, renders the hero header banner, and provides HTML wrapper helpers for metric card sections. Path resolved with `os.path.abspath(__file__)`.

### Application Controller (`app.py`)
Streamlit multi-stage UI controller with the following flow:

1. **File Upload** — accepts CSV, XLSX, PDF via `Data/loader.py`.
2. **Column Mapping** — displays `map_columns` predictions in a dropdown UI; user confirms or overrides; duplicate mapping collisions blocked.
3. **Data Pipeline** — on confirmation: renames columns, runs `clean_data`, runs `run_validation`. Blocking failures halt the UI; warnings shown in sidebar.
4. **Metric Source Selection** — if derived metric discrepancies detected, user chooses uploaded vs calculated metrics.
5. **Analytics Dashboard** — calls `run_analytics_pipeline`, `prepare_graph_data`, `generate_kpi_summary`, `generate_best_performers`, `build_ai_summary`, and renders all charts and tables.
6. **AI Consultant Tab** — accepts natural language questions, calls `generate_ai_response` with the summary context.
7. **Qualitative Analysis Tab** — accepts a separate ad copy CSV, runs the qualitative column mapping UI, cleans text data, runs `text_analysis`, and displays readability diagnostics.

---

## 4. Key Data Flow Summary

```
Upload CSV
  → Data/loader.py        (raw DataFrame)
  → map_columns()         (predicted header mapping dict)
  → [User confirms mapping in UI]
  → df.rename()           (canonical column names)
  → clean_data()          (type-safe, clean DataFrame)
  → run_validation()      (combined validation report)
  → run_analytics_pipeline()
      → kpi, campaigns, audience, devices, objectives,
        time, funnel, anomalies
      → generate_business_insights()
      → generate_action_recommendations()
  → prepare_graph_data()  (Plotly-ready series/frames)
  → UI renders charts, tables, KPIs
  → build_ai_summary()    (AI context payload)
  → generate_ai_response(user_question, summary)  ← Gemini API
```

RAG Ad Copy Pipeline (independent of above):
```
knowledge_base/*.md
  → generate_chunks()     (heading-keyed dict)
  → embed_document_chunks()  (Gemini embeddings)
  → add_documents_to_vector_store()  (ChromaDB)
  ← user_query
  → embed_query()         (query vector)
  → top_k()               (nearest chunks)
  → generate_prompt()     (full RAG prompt)
  → llm_response.py       (stub → future Gemini call)
```

---

## 5. Coding & Quality Standards

- **Single Responsibility Principle**: Every package and file has exactly one responsibility.
- **Type Hints**: All public functions carry full input and return type annotations.
- **Docstrings**: NumPy/Google-style docstrings with Parameters, Returns, and Raises sections.
- **Logging**: `logging.getLogger(__name__)` in every module. `ERROR` logged before every raised exception. `INFO` for pipeline milestones. `WARNING` for non-fatal skips. Exception swallowing is prohibited.
- **Path Portability**: All internal file paths (ChromaDB store, knowledge base) are resolved relative to `__file__` using `pathlib.Path`, not hardcoded absolute paths.
- **Environment Variables**: `GEMINI_API_KEY` loaded via `python-dotenv` at call time. Never hardcoded. `.env.example` provided as reference.
- **Edge Case Guards**: All public AI pipeline functions validate inputs (empty strings, empty lists, wrong types, missing keys) before making external calls.
