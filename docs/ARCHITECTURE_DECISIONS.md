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
