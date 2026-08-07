================================================================================
          📊 AI MARKETING CAMPAIGN ANALYTICS PLATFORM
================================================================================

Empowering marketing teams with precision campaign analytics, automated data validation, 
segmented cohort insights, and AI-driven strategic guidance.

--------------------------------------------------------------------------------
🌟 EXECUTIVE OVERVIEW
--------------------------------------------------------------------------------
The AI Marketing Campaign Analytics Platform is an end-to-end, production-grade 
analytics system engineered to ingest raw marketing campaign CSVs, validate data 
integrity, clean structural anomalies, calculate multi-dimensional KPI cohorts, and 
generate visual analytics dashboards alongside an interactive AI Consultant powered by 
Google Gemini.

Whether analyzing budget efficiency, audience segment performance, or creative fatigue, 
the platform converts messy marketing data into actionable growth strategies in seconds.

--------------------------------------------------------------------------------
✨ KEY FEATURES & CAPABILITIES
--------------------------------------------------------------------------------

📋 1. INTELLIGENT COLUMN MAPPING & INGESTION
   - Dynamic Header Resolution: Automatically maps arbitrary CSV headers to canonical 
     metrics using fuzzy matching and pre-defined alias dictionaries.
   - Collision Detection: Prevents duplicate column mappings to maintain dataset 
     schema integrity.

🛡️ 2. COMPREHENSIVE 6-STAGE DATA VALIDATION ENGINE
   Runs complete diagnostic pipeline checks BEFORE data cleaning:
   - Schema Validation: Ensures presence of mandatory metrics (spend_inr, clicks, 
     impressions, date).
   - Missing Value Analysis: Assesses missing cell density across columns, flags 
     completely empty headers, and warns on sparse rows.
   - Duplicate Row Detection: Identifies and logs identical data records with full 
     row visualization.
   - Business Logic Audit: Enforces logical boundary rules (e.g. impressions >= reach, 
     clicks <= impressions, conversions <= clicks, non-negative values).
   - Derived Metric Discrepancy Reconciliation: Compares user-uploaded derived columns 
     (CTR, CPC, Conversion Rate) against system-calculated values and provides an 
     interactive resolution selector.

🧹 3. PURE DATA CLEANING & COERCION
   - Flexible Date Parsing: Handles mixed date formats (2024-01-01, 01/02/2024, ISO 
     strings) with coercion guards.
   - Currency & Numeric Sanitization: Automatically strips currency symbols (₹, $) 
     and formatting commas (1,500.50) into clean float types.
   - Missing Value Imputation: Safely imputes missing values to prevent downstream 
     division-by-zero errors.

📊 4. MULTI-DIMENSIONAL COHORT & KPI ANALYTICS
   - Core KPI Aggregations: Computes Spend, Reach, Impressions, Clicks, Conversions, 
     CTR, CPC, CPM, and Conversion Rates.
   - Cohort Segmentations: Aggregates performances across Age Group, Gender, Device Type, 
     and Campaign Objectives.
   - Top Performer Identification: Highlights top campaigns by Conversions, Spend 
     Efficiency, and CTR.

🎨 5. EXECUTIVE UI & INTERACTIVE PLOTLY CHARTS
   - Tiered Metric Cards: Executive dashboard featuring top primary metrics alongside 
     operational grids.
   - Glassmorphism Aesthetic: Modern executive dark design powered by Plus Jakarta Sans 
     typography.
   - Interactive Visualizations: Custom Plotly bar charts, line trends, scatter plots 
     (Cost Efficiency), and donut charts.

🤖 6. AI CONSULTANT INTEGRATION
   - Context-Aware Analytics: Aggregates structured campaign data summaries as context 
     for Google Gemini.
   - Strategic Q&A: Asks natural language questions regarding budget reallocation, 
     creative updates, and audience targeting.

--------------------------------------------------------------------------------
🏛️ SYSTEM ARCHITECTURE
--------------------------------------------------------------------------------
The project strictly follows Clean Architecture and the Single Responsibility Principle (SRP):

market_data_analyzer/
├── assets/                  # Sample datasets and test resources
│   └── sample_data/
├── config/                  # Central configuration & canonical schema definitions
│   ├── __init__.py
│   └── settings.py
├── data/                    # Data ingestion & multi-parameter filtering
│   ├── __init__.py
│   ├── loader.py
│   └── filter.py
├── mapping/                 # Header normalization & column mapping predictions
│   ├── __init__.py
│   └── column_mapper.py
├── cleaning/                # Pure data type standardization & value coercion
│   ├── __init__.py
│   └── data_cleaner.py
├── validation/              # Strict schema, structural, & business logic validators
│   ├── __init__.py
│   ├── schema_validator.py
│   ├── structural_validator.py
│   ├── duplicate_validator.py
│   ├── missing_value_validator.py
│   ├── duplicate_row_validator.py
│   ├── business_logic_validator.py
│   ├── derived_metric_validator.py
│   └── validator.py
├── analytics/               # Metrics calculations, segmentations, & anomaly detection
│   ├── __init__.py
│   ├── analytics_engine.py  # Master analytics orchestrator
│   ├── utils.py             # Reusable math and formatting blocks
│   ├── kpi.py               # Account level KPIs
│   ├── campaign_analysis.py # Campaign specific performance metrics
│   ├── audience_analysis.py # Age & gender breaks
│   ├── device_analysis.py   # Desktop, Mobile, Tablet analysis
│   ├── objective_analysis.py# Campaign objective analyses
│   ├── time_analysis.py     # Timeline trends & directions
│   └── anomaly_detection.py # Critical, warning & minor anomaly rules
├── insights/                # Formatting display-ready metrics & recommendations
│   ├── __init__.py
│   ├── insight_engine.py    # Interprets what happened & why it matters
│   ├── recommendation_engine.py # Strategic actions decision engine
│   └── summary_builder.py   # AI context summary builder
├── ai/                      # Google Gemini API integration module
│   ├── __init__.py
│   └── ai_engine.py
├── visualization/           # Plotly chart factories & custom dark theme
│   ├── __init__.py
│   └── charts.py
├── docs/                    # Architectural decision records & handbook
│   ├── PROJECT_HANDBOOK.md
│   └── ARCHITECTURE_DECISIONS.md
├── app.py                   # Main Streamlit Orchestrator Application
├── .gitignore
├── .env.example
├── requirements.txt         # Project dependencies
└── README.txt               # Plain text project guide & documentation

--------------------------------------------------------------------------------
🚀 QUICK START GUIDE
--------------------------------------------------------------------------------

📋 Prerequisites:
   - Python 3.10+ installed on your system.
   - A Google Gemini API Key (for AI Consultant features). 
     Get one at https://aistudio.google.com/

🛠️ Installation & Execution Steps:

   1. Clone or navigate to repository:
      cd market_data_analyzer

   2. Set up environment variable for Google Gemini API:
      # On Linux/macOS:
      export GEMINI_API_KEY="your_actual_gemini_api_key_here"

      # On Windows (PowerShell):
      $env:GEMINI_API_KEY="your_actual_gemini_api_key_here"

   3. Install dependencies:
      pip install -r requirements.txt
      
      # Or via pipenv:
      pipenv install

   4. Launch the Streamlit application:
      streamlit run app.py
      
      # Or via pipenv:
      pipenv run streamlit run app.py

   5. Access dashboard in browser:
      Open http://localhost:8501

--------------------------------------------------------------------------------
💻 WORKFLOW & USAGE
--------------------------------------------------------------------------------
1. Upload Dataset: Upload your campaign CSV file on the landing view (or use sample 
   CSVs in assets/sample_data/).
2. Confirm Column Mapping: Review and verify detected column mappings against canonical 
   metric headers.
3. Inspect Diagnostics: Check non-blocking validation logs for duplicate rows, missing 
   fields, or derived metric discrepancies.
4. Explore Overview Dashboard: Review top KPI highlight cards, best performer campaigns, 
   and interactive Plotly trend graphs.
5. Analyze Cohorts: Inspect breakdown tables and charts by Gender, Age Group, Device, 
   and Campaign Objective.
6. Review Actionable Advice: Examine automated recommendations for Budget Reallocation, 
   Spend Reduction, Creative Updates, and Landing Page optimization.
7. Consult AI Assistant: Type custom questions to receive AI-powered marketing strategy 
   recommendations.

--------------------------------------------------------------------------------
🔬 TESTING & VALIDATION
--------------------------------------------------------------------------------
Run compilation tests across all packages:
python -m py_compile app.py config/*.py data/*.py mapping/*.py cleaning/*.py validation/*.py analytics/*.py insights/*.py ai/*.py visualization/*.py

--------------------------------------------------------------------------------
📜 DOCUMENTATION & REFERENCES
--------------------------------------------------------------------------------
For deeper insights into system decisions and design principles:
- docs/PROJECT_HANDBOOK.md       : Comprehensive guide on package architecture and guidelines.
- docs/ARCHITECTURE_DECISIONS.md : Architecture Decision Records (ADR).

--------------------------------------------------------------------------------
📄 LICENSE
--------------------------------------------------------------------------------
Distributed under the MIT License.
================================================================================
