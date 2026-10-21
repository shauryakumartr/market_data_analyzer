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
Reorganized the codebase into highly modular, decoupled packages (`config/`, `Data/`, `mapping/`, `cleaning/`, `validation/`, `analytics/`, `insights/`, `ai/`, `visualization/`) and created a thin entry point controller at the root (`app.py`).

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
Replaced the hardcoded key with `os.environ.get("GEMINI_API_KEY")` and added a `.env.example` file. All AI modules load the key via `python-dotenv` at call time.

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
- Split aggregations into decoupled modules: `kpi.py`, `campaign_analysis.py`, `audience_analysis.py`, `device_analysis.py`, `objective_analysis.py`, `time_analysis.py`, `funnel_analysis.py`, and `anomaly_detection.py`.
- Formed the master `analytics_engine.py` orchestrator to run the entire suite and return a single combined analytics report.
- Re-architected `insights/insight_engine.py` to translate metrics to qualitative facts ("what happened" & "why it matters" — no math) and `insights/recommendation_engine.py` to compile action recommendations using deterministic rules across four priority tiers (Critical, High, Medium, Low).

**Reason**:  
Enforces strict Single Responsibility Principle (SRP) where calculators compute, insight engines explain, recommendation engines suggest actions, and the orchestrator aggregates.

**Advantages**:  
- Business logic is completely separated from mathematical calculations.
- Code readability is maximized.
- High testability; any single analytical block can be mocked or unit-tested in isolation.

**Disadvantages**:  
- Slightly increased call depth for simple analytics queries.

---

## Decision 5: RAG Knowledge Base Chunker Implementation

**Context**:  
The AI needed to be contextually aware of marketing frameworks and rules (like direct response frameworks, mobile feed rules, and readability diagnostics) but passing entire raw markdown documents to the LLM exceeds token limits or causes loss of context.

**Problem**:  
- The original `chunker.py` was a stub with hardcoded paths.
- No error handling, logging, or type hints.
- Could not process multiple files or chunk them intelligently.

**Decision Taken**:  
Implemented a robust `generate_chunks` function in `ai/chunker.py`. It uses regular expressions to split specific markdown files based on H2 (`##`) headers. Returns `Dict[str, {"content": str, "source": str}]` — the heading is the key, the chunk body and source filename are the value dict.

**Reason**:  
Provides a structured list of textual chunks that can easily be embedded and retrieved for the RAG pipeline. Heading-keyed dict aligns naturally with the `title` parameter of the Gemini embedding API's `EmbedContentConfig`.

**Advantages**:  
- Graceful error handling if files are missing.
- Contextual chunks that represent independent logical sections.
- Easily extensible to new markdown rules documents.
- Collision handling for duplicate headings via counter suffixes.

**Disadvantages**:  
- Simple splitting strategy might still create overly large chunks if a section under `##` is too long.

**Scalability Impact**: Positive. Can be integrated with a vector database.  
**Maintainability Impact**: Positive. Standardized chunking logic.  
**Testing Impact**: Easy to mock file reads and test regex logic.

---

## Decision 6: ChromaDB as the Vector Store with Inner Product Space

**Context**:  
The RAG pipeline requires a local, persistent vector store to store knowledge base embeddings and retrieve the most relevant chunks at query time without an external service dependency.

**Problem**:  
- The application needs a portable, file-based vector store that works offline.
- Cosine similarity vs inner product distance must match the Gemini embedding model's expected comparison method.

**Decision Taken**:  
Used `chromadb.PersistentClient` with `hnsw:space=ip` (inner product) in the collection metadata. The store is persisted under `assets/vector_store/`, resolved via `pathlib.Path(__file__)` so it works on any machine without hardcoded paths.

**Reason**:  
ChromaDB is lightweight, embeds directly into the Python process, and supports persistent on-disk storage. Inner product is the correct similarity metric for the Gemini embedding model.

**Alternative Approaches Considered**:  
Pinecone (cloud), FAISS (in-memory only), Weaviate (requires Docker).

**Why Rejection**:  
Cloud services add latency and key management overhead. FAISS is in-memory only (no persistence). Weaviate requires a separate running process.

**Advantages**:  
- Zero external infrastructure.
- Portable file-based persistence.

**Disadvantages**:  
- Not suitable for large-scale multi-user deployments.

**Scalability Impact**: Acceptable for single-user / small-team workloads.  
**Maintainability Impact**: Positive. The store regenerates from the markdown source with a single pipeline run.

---

## Decision 7: Portable File Path Resolution via `pathlib.Path(__file__)`

**Context**:  
Several AI pipeline modules (`vector_store.py`, `top_k.py`, `chunker.py`) originally contained hardcoded absolute paths specific to the original developer's machine (e.g., `/home/shaw/Documents/market_analyzer/assets/vector_store`).

**Problem**:  
- Any collaborator cloning the repository on a different machine would encounter `FileNotFoundError` immediately.
- Hardcoded paths make containerisation and CI/CD impossible.

**Decision Taken**:  
Replaced all hardcoded absolute paths with `pathlib.Path(__file__).resolve().parent.parent / "assets" / "..."` computed at module import time. Module-level constants (`_DEFAULT_DB_PATH`, `_DEFAULT_KB_DIR`) hold the resolved paths.

**Reason**:  
`__file__` is always the absolute path of the current module file regardless of the machine or working directory. Navigating relative to it guarantees correctness.

**Advantages**:  
- Works on any machine or OS without configuration.
- Portable for Docker containers and CI environments.

**Disadvantages**:  
- Slight indirection compared to a simple string constant.

**Scalability Impact**: Positive. No per-developer setup required.  
**Maintainability Impact**: Highly positive. One less category of onboarding bug.

---

## Decision 8: Qualitative Ad Copy Analysis Module

**Context**:  
The platform originally focused exclusively on quantitative campaign metrics (spend, CTR, CPC). A second dimension of analysis was added to evaluate the quality of ad copy text.

**Problem**:  
- Poor ad copy readability and formatting are major drivers of poor CTR and conversion rates that quantitative KPIs alone cannot diagnose.
- No existing module analyzed text-level features of ads.

**Decision Taken**:  
Created `analytics/qualitative_analysis.py` with `text_analysis(df)` as the public entry point. Uses `textstat` for Flesch-Kincaid grade and sentence complexity, `emoji` library for emoji count and density, and precompiled regex patterns for offer/urgency detection. Applies a micro-copy guardrail (<10 words) that skips readability scoring for very short texts.

**Reason**:  
Direct-response copywriting quality is measurable through objective criteria (reading grade, mobile truncation, wall-of-text detection). These diagnostics map directly to the knowledge base rules in the RAG system.

**Advantages**:  
- Actionable per-ad diagnostics.
- Tightly aligned with knowledge base content (mobile feed rules, readability diagnostics).
- Completely decoupled from the quantitative analytics pipeline.

**Disadvantages**:  
- Requires `textstat` and `emoji` as additional dependencies.
- `textstat` accuracy degrades on very short copy fragments.

**Scalability Impact**: Positive. New text metrics can be added to `_analyze_single_text` without changing the public API.  
**Maintainability Impact**: Positive. Single-responsibility text analysis function with guardrail fallbacks.
