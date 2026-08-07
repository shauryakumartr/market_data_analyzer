# AI Marketing Analytics Platform
## Engineering Handbook v3.0

---

## 1. Project Overview

This is a modular, production-quality AI Marketing Analytics Platform designed to ingest raw marketing campaign CSVs, match fields dynamically, validate schema & structural rules, clean dirty rows, perform advanced KPIs & segmented cohort calculations, and present data-rich visual dashboards alongside an AI consultant powered by Google Gemini.

---

## 2. Restructured Modular Architecture

The project has been migrated into well-defined, highly cohesive packages:

```
market_data_analyzer/
├── assets/                  # Sample datasets and resources
│   └── sample_data/
├── config/                  # Configuration settings and constant mappings
│   ├── __init__.py
│   └── settings.py
├── data/                    # Reading, parsing, and filtering data
│   ├── __init__.py
│   ├── loader.py
│   └── filter.py
├── mapping/                 # Canonical column header mapping
│   ├── __init__.py
│   └── column_mapper.py
├── cleaning/                # Standardization and type coercion (pure cleaning)
│   ├── __init__.py
│   └── data_cleaner.py
├── validation/              # Strict schema and validation rules
│   ├── __init__.py
│   ├── schema_validator.py
│   ├── structural_validator.py
│   ├── duplicate_validator.py
│   ├── missing_value_validator.py
│   ├── duplicate_row_validator.py
│   ├── business_logic_validator.py
│   ├── derived_metric_validator.py
│   └── validator.py
├── analytics/               # Metrics, KPI, segmentation, and anomaly detection
│   ├── __init__.py
│   ├── analytics_engine.py  # Orchestrates all analytical runs
│   ├── utils.py             # Math and formatting helper blocks
│   ├── kpi.py               # Global account KPIs
│   ├── campaign_analysis.py # Campaign specific performance metrics
│   ├── audience_analysis.py # Age & gender breakdowns
│   ├── device_analysis.py   # Device breakdowns (Desktop/Mobile/Tablet)
│   ├── objective_analysis.py# Objective breakdowns
│   ├── time_analysis.py     # Timeline trends & directions
│   └── anomaly_detection.py # Multi-severity anomaly rules engine
├── insights/                # Preparation of display-ready insights
│   ├── __init__.py
│   ├── insight_engine.py    # Interprets what happened & why it matters
│   ├── recommendation_engine.py # Proposes strategic actions using business rules
│   └── summary_builder.py   # AI context formatter
├── ai/                      # AI integration with Google Gemini
│   ├── __init__.py
│   └── ai_engine.py
├── visualization/           # Plotly chart factories & dark theme layouts
│   ├── __init__.py
│   └── charts.py
├── docs/                    # System documentation & architectural logs
│   ├── PROJECT_HANDBOOK.md
│   └── ARCHITECTURE_DECISIONS.md
├── app.py                   # Streamlit Orchestrator UI (Executive Controller)
├── .gitignore
├── .env.example
├── README.txt               # Plain text project guide & documentation
└── requirements.txt
```

---

## 3. Package Responsibilities

### Config (`config/`)
- Single source of truth for column sets (`MANDATORY_COLUMNS`, `OPTIONAL_COLUMNS`, `DERIVED_COLUMNS`), aliases for mapper matching, numeric standard types, and UI options.

### Data Handling (`data/`)
- Loading files and raw CSV streams.
- Applying user selections copy-safely.

### Mapping (`mapping/`)
- Pre-computing initial column mapping matches based on normalized headers and aliases.

### Cleaning (`cleaning/`)
- Performing conversions, null filling, duplicate removal, and stripping formatting.

### Validation (`validation/`)
- Verifies system inputs: Schema presence, structural validity, row count checks, collision detection for mappings, missing values assessment, duplicate row checks, business rule validation, and derived metrics discrepancies.

### Analytics (`analytics/`)
- Orchestrated by `analytics_engine.py`. Under no circumstances does this module create recommendations or format graphs.
- Contains independent modules for computing account-level KPIs, campaign segments, demographics cohorts, device shares, timeline trend series, and severity-sorted performance anomalies.

### Insights (`insights/`)
- Converts raw metrics into decorated formats (formatting currency, rounding percentages, grouping tables) for the dashboard.
- `insight_engine.py` interprets metrics to qualitative "What happened" and "Why it matters" text.
- `recommendation_engine.py` proposes tactical actions based on data.
- Summarizes analytical context into standard schemas for the AI.

### AI Engine (`ai/`)
- Communicates safely with Google Gemini API using environment variables.

### Visualization (`visualization/`)
- Returns clean Plotly figures based on chart types.

---

## 4. Coding & Quality Standards

- **Single Responsibility Principle**: Every package and file has one task.
- **Type Hints**: All functions specify input and return type declarations.
- **Docstrings**: Professional descriptive header blocks explaining arguments and return values.
- **Logging**: Standard library logging is utilized for key execution thresholds. Swallowing exceptions is prohibited.
