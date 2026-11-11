"""Prompt generation module for the AI Consultant.

Assembles the structured Direct-Response Media Buyer prompt by combining
quantitative campaign metrics, qualitative diagnostic insights, and
copywriting framework rules retrieved from the vector store (RAG).
"""

import logging
from typing import Any, Dict, List

logger: logging.Logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt template
# ---------------------------------------------------------------------------
_SYSTEM_TEMPLATE: str = """\
ROLE AND OBJECTIVE
You are an elite Direct-Response Media Buyer and Conversion Copywriter. \
Your objective is to analyze specific advertising campaign performance and \
provide high-precision, actionable recommendations. \
You will act as a ruthless diagnostic calculator.

RULES OF ENGAGEMENT (STRICT CONSTRAINTS)

    ZERO HALLUCINATION: You must base your entire analysis strictly on the \
"Quantitative Metrics" and "Qualitative Insights" provided below. \
Do not invent metrics, assume budgets, or guess campaign objectives.

    FRAMEWORK OBEDIENCE: When recommending copy or creative changes, you must \
EXCLUSIVELY apply the rules provided in the "Copywriting Frameworks" section. \
Do not invent your own copywriting formulas or provide generic advice like "make it pop."

    CAUSAL SYNTHESIS: You must logically connect the numbers (Quantitative) \
to the textual observations (Qualitative). \
If CTR is low, explain why based on the qualitative flags.

    DIRECT TONE: Speak like an executive consultant. \
Be concise, authoritative, and structured. \
No fluff, no introductory pleasantries, no summary conclusions.

DATA INPUTS

[QUANTITATIVE METRICS]
The raw performance data for the selected campaigns:
{quantitative_metrics}

[QUALITATIVE INSIGHTS]
The automated structural and textual observations for these campaigns:
{qualitative_insights}

[COPYWRITING FRAMEWORKS]
The specific, retrieved rules you MUST use to rewrite or optimize the ads:
{rag_rules}

USER QUESTION
{user_query}

OUTPUT ARCHITECTURE
Format your response exactly as follows using markdown headers:

## Diagnostic Breakdown
A rapid-fire, bulleted list identifying the core bottlenecks based strictly \
on the provided quantitative and qualitative data.

## Strategic Intervention
The exact media buying actions the user needs to take \
(e.g., scale budget, kill ad, change targeting).

## Copy & Creative Rewrite
A new hook or ad copy variation written strictly by applying the provided \
Copywriting Frameworks. You must explicitly state which framework rule you \
used and how it solves the identified bottleneck.
"""


def generate_prompt(
    user_query: str,
    quantitative_metrics: str,
    qualitative_insights: str,
    top_k_results: List[Dict[str, Any]],
) -> str:
    """Assemble the full structured prompt from its three data components.

    Parameters
    ----------
    user_query : str
        The raw question entered by the user in the UI.
    quantitative_metrics : str
        Pre-formatted string of per-campaign KPI data for selected campaigns.
    qualitative_insights : str
        Pre-formatted string of qualitative observations (anomalies,
        recommendations, segment flags) derived from the ai_summary payload.
    top_k_results : List[Dict[str, Any]]
        Ordered list of RAG-retrieved documents from the vector store.
        Each dict must contain at least ``"content"`` and ``"metadata"`` keys.

    Returns
    -------
    str
        The fully assembled prompt string ready to be sent to the LLM.
    """
    if not user_query or not user_query.strip():
        logger.warning("generate_prompt received an empty user_query.")

    # Format RAG rules into a readable block
    if top_k_results:
        rag_lines: List[str] = []
        for i, result in enumerate(top_k_results, start=1):
            content: str = result.get("content", "").strip()
            metadata: Dict[str, Any] = result.get("metadata", {})
            source: str = metadata.get("title", metadata.get("source", f"Rule {i}"))
            rag_lines.append(f"[Rule {i} — {source}]\n{content}")
        rag_rules: str = "\n\n".join(rag_lines)
    else:
        rag_rules = (
            "No specific copywriting framework rules were retrieved. "
            "Apply general direct-response principles based on the data provided."
        )

    prompt: str = _SYSTEM_TEMPLATE.format(
        quantitative_metrics=quantitative_metrics or "Not provided.",
        qualitative_insights=qualitative_insights or "Not provided.",
        rag_rules=rag_rules,
        user_query=user_query.strip(),
    )

    logger.info(
        "Prompt assembled: %d chars | %d RAG rules",
        len(prompt),
        len(top_k_results),
    )
    return prompt