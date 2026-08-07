# Architecture Decisions Log

This document records the architectural decisions made during the lifecycle of the AI Marketing Analytics Platform.

---

## Decision 1: Project Restructuring to Clean Architecture

**Context**:  
The legacy codebase was structured as a flat set of scripts in `/Data/` with highly coupled functions. There was no division between data ingestion, validation, business calculations, presentation formatting, and UI generation.

**Problem**:  
- Violations of the Single Responsibility Principle: cleaning code was doing anomaly detection, and UI code was doing calculations and plotting.
- Inability to write tests without spinning up a Streamlit runtime.
- High risk of regressions during code changes.

**Decision Taken**:  
Reorganized the codebase into highly modular, decoupled packages (`config/`, `data/`, `mapping/`, `cleaning/`, `validation/`, `analytics/`, `insights/`, `ai/`, `visualization/`) and created a thin entry point controller at the root (`app.py`).

**Reason**:  
Isolates dependencies, simplifies testing, makes code paths predictable, and strictly aligns with the PROJECT_HANDBOOK.md.

**Alternative Approaches Considered**:  
Keep the flat directory structure but modularize files.

**Why Rejection**:  
Flat directories make it harder to enforce folder boundaries and dependencies.

**Advantages**:  
- Separation of concerns.
- Clear import directories.
- Clean and testable APIs.

**Disadvantages**:  
- More directories and files to manage.

**Scalability Impact**: Highly positive. New analysis modules or visualizations can be added independently.  
**Maintainability Impact**: Highly positive. Isolation allows developers to focus on specific layers.  
**Testing Impact**: Highly positive. Pure functions can be unit-tested without external wrappers.  
**Future Considerations**: Future UI packages (e.g., FastAPI backend or React frontend) can reuse the backend libraries directly.

---

## Decision 2: Environment Variable Configuration for API Credentials

**Context**:  
The legacy AI handling code contained a hardcoded Google Gemini API key committed in plaintext.

**Problem**:  
- Security vulnerability: committing api keys to version control exposes access.
- Non-scalable: key rotations require source code edits.

**Decision Taken**:  
Replaced the hardcoded key with `os.environ.get("GEMINI_API_KEY")` and added a `.env.example` file.

**Reason**:  
Secures the key, respects 12-factor app design principles, and allows easy container deployment configurations.

**Alternative Approaches Considered**:  
Use Streamlit secrets.

**Why Rejection**:  
Streamlit secrets coupling makes the code dependent on Streamlit runtime, breaking clean library boundaries.

**Advantages**:  
- Portable and secure.

**Disadvantages**:  
- Developer must manually define environment variables or run a dotenv setup.

**Scalability Impact**: Positive. Supports standard production environments.  
**Maintainability Impact**: Positive. Decoupled configurations.  
**Testing Impact**: Easy mocking of keys in unit test environments.

---

## Decision 3: Decoupled Advanced Validation Layer

**Context**:  
The legacy codebase performed basic numeric filtering inside the cleaning module. There was no distinct missing value logic, duplicate row checks, or derived metric validation.

**Problem**:  
- Violations of the Single Responsibility Principle: the cleaning phase modified data under silent logical rules, which hid errors from the user rather than validating them.
- User could not compare discrepancies in their uploaded calculations.

**Decision Taken**:  
Separated all validation layers into individual sub-modules (`validation/missing_value_validator.py`, `validation/duplicate_row_validator.py`, `validation/business_logic_validator.py`, `validation/derived_metric_validator.py`). Removed business logic filters from `cleaning/data_cleaner.py`. Introduced a derived metric comparison selection interface in the app UI.

**Reason**:  
Provides structural error diagnostics to the user, preserves the integrity of the raw dataset during the mapping phase, and enforces strict separation of concerns.

**Alternative Approaches Considered**:  
Keep logical row drops inside `clean_data.py` and output warnings there.

**Why Rejection**:  
Violates the handbook design principle that cleaning should never validate business rules or generate warnings.

**Advantages**:  
- Clear diagnostic warnings for users.
- Cleaners are pure and simple.
- Discrepancy selection gives user ownership of metric sources.

**Disadvantages**:  
- Extra validation computations before cleaning.

**Scalability Impact**: Highly positive. New business rules can be added as validation metrics without altering cleaner logic.  
**Maintainability Impact**: Positive. Clear debugging boundaries for bad data.  
**Testing Impact**: Unit tests can run checks on validators directly.

---

## Decision 4: Modular Analytics Restructuring and Pipeline Orchestration

**Context**:  
Analytics logic was scattered across coupled, partially completed segmentation files, and calculators in `analytics/`. There was no distinct orchestrator mapping the inputs and outputs, leading to presentation code carrying too much formatting and calculation burden.

**Problem**:  
- Calculation logic (CTR, CPC) was repeated across segmentation algorithms.
- Interpretation logic was mixed up, and recommendation criteria were not clearly decoupled from business KPIs.
- Streamlit application layer directly called separate calculator utilities, complicating testing and validation.

**Decision Taken**:  
Restructured `analytics/` and `insights/` package to partition calculations and logic interpretability.
- Created `analytics/utils.py` containing math and formatting building blocks.
- Split aggregations into decoupled modules: `kpi.py`, `campaign_analysis.py`, `audience_analysis.py`, `device_analysis.py`, `objective_analysis.py`, `time_analysis.py`, and `anomaly_detection.py`.
- Formed the master `analytics_engine.py` orchestrator to run the entire suite and return a single `analytics_report` object.
- Re-architected `insights/insight_engine.py` to translate metrics to text ("what happened" & "why it matters" only, no math) and `insights/recommendation_engine.py` to compile action recommendations using deterministic rules.

**Reason**:  
Enforces strict Single Responsibility Principle (SRP) where calculators compute, insight engines explain, recommendation engines suggest actions, and the orchestrator aggregates.

**Advantages**:  
- Business logic is completely separated from mathematical calculations.
- Code readability is maximized.
- High testability; any single analytical block can be mocked or unit-tested in isolation.
