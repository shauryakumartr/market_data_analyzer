# AI Marketing Analytics Platform
## Engineering Handbook v2.0

---

## 1. Project Overview

This is a modular, production-quality AI Marketing Analytics Platform designed to ingest raw marketing campaign CSVs, match fields dynamically, validate schema & structural rules, clean dirty rows, perform advanced KPIs & segmented cohort calculations, and present data-rich visual dashboards alongside an AI consultant powered by Google Gemini.

---

## 2. Restructured Modular Architecture

The project has been migrated from a flat directory structure into well-defined, highly cohesive packages:

```
project/
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
├── cleaning/                # Standardization and type management (no anomalies)
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
│   ├── kpi_calculator.py
│   ├── performance.py
│   ├── segmentation.py
│   ├── graph_data.py
│   └── anomaly_detector.py
├── insights/                # Preparation of display-ready insights
│   ├── __init__.py
│   ├── insight_engine.py
│   ├── recommendations.py
│   └── summary_builder.py
├── ai/                      # AI integration with Google Gemini
│   ├── __init__.py
│   └── ai_engine.py
├── visualization/           # Plotly chart factories
│   ├── __init__.py
│   └── charts.py
├── docs/                    # System documentation
│   ├── PROJECT_HANDBOOK.md
│   └── ARCHITECTURE_DECISIONS.md
├── app.py                   # Streamlit Orchestrator UI (Thin Controller)
├── .gitignore
├── .env.example
└── requirements.txt
```

---

## 3. Package Responsibilities

### Config (`config/`)
- Single source of truth for column sets (`MANDATORY_COLUMNS`, `OPTIONAL_COLUMNS`, `DERIVED_COLUMNS`), aliases for mapper matching, numeric standard types, and UI options.

### Data Handling (`data/`)
- Loading files and raw CSV streams.
- Applying user selections (Objective, Device, Gender, Age Group, Date Range) copy-safely.

### Mapping (`mapping/`)
- Pre-computing initial column mapping matches based on normalized headers and aliases.

### Cleaning (`cleaning/`)
- Performing conversions, null filling, duplicate removal, and stripping formatting.
- Under no circumstances does this module identify business anomalies.

### Validation (`validation/`)
- Verifies system inputs: Schema presence, structural validity, row count checks, collision detection for mappings, missing values assessment, duplicate row checks, business rule validation, and derived metrics discrepancies.

### Analytics (`analytics/`)
- Calculates raw metrics: KPI aggregations, segment cohorts, graph dimensions, performance ranks, and business rule anomaly detection.

### Insights (`insights/`)
- Converts raw metrics into decorated formats (formatting currency, rounding percentages, grouping tables, mapping recommendations) for the dashboard.
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
