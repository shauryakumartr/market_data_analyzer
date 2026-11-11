"""Module for interacting with the Google Gemini API to generate insights.

Sends structured analytics summaries and natural language prompts to Google Gemini AI models
to produce executive marketing consultation insights.

Two entry points are exposed:

* ``generate_ai_response`` — legacy simple call used by older code paths.
* ``generate_structured_ai_response`` — full RAG-augmented call that uses the
  Direct-Response Media Buyer prompt template, quantitative metrics,
  qualitative insights, and retrieved copywriting framework rules.
"""

import os
import json
import logging
from typing import Any, Dict, List, Optional

# Module-level logger for Gemini AI engine operations
logger: logging.Logger = logging.getLogger(__name__)

_GEMINI_MODEL: str = "gemini-2.5-flash"
_MAX_OUTPUT_TOKENS: int = 2048


def _get_api_key() -> str:
    """Retrieve and validate the Gemini API key from the environment.

    Returns
    -------
    str
        The API key string.

    Raises
    ------
    ValueError
        If the GEMINI_API_KEY environment variable is not set.
    """
    api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set")
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please configure it in your environment or .env file."
        )
    return api_key


def _get_genai_client(api_key: str) -> Any:
    """Initialise and return a google-genai client.

    Parameters
    ----------
    api_key : str
        Gemini API key.

    Returns
    -------
    Any
        Configured genai.Client instance.

    Raises
    ------
    RuntimeError
        If the google-genai package is not installed.
    """
    try:
        from google import genai  # type: ignore
        return genai.Client(api_key=api_key)
    except ImportError:
        logger.error("google-genai package is not installed in the python environment")
        raise RuntimeError(
            "The google-genai package is required for AI features. "
            "Install it via: pip install google-genai"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ai_response(prompt: str, summary: Dict[str, Any]) -> str:
    """Generate an AI-powered marketing analysis response using Google Gemini API.

    Legacy simple call: serialises the full ``summary`` dict as context and
    sends it alongside the user ``prompt``.

    Parameters
    ----------
    prompt : str
        User's question or analytical query.
    summary : Dict[str, Any]
        Compiled analytics summary payload for model context grounding.

    Returns
    -------
    str
        AI-generated executive response text.

    Raises
    ------
    ValueError
        If GEMINI_API_KEY environment variable is not configured.
    RuntimeError
        If google-genai dependency is missing or API invocation fails.
    """
    api_key: str = _get_api_key()
    logger.info(
        "Initiating legacy AI response generation for prompt length %d chars",
        len(prompt),
    )

    client = _get_genai_client(api_key)
    summary_str: str = json.dumps(str(summary))

    try:
        response: Any = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=(
                f"Act as a business consultant. Answer the following question "
                f"based ONLY on the provided data. Do not invent or modify data.\n\n"
                f"DATA:\n{summary_str}\n\n"
                f"QUESTION: {prompt}\n\n"
                f"Write at least 200 to 300 words."
            ),
            config={"max_output_tokens": 500},
        )
        logger.info("AI response generated successfully")
        return str(response.text)
    except Exception as exc:
        logger.error("AI API call failed: %s", exc)
        raise RuntimeError(f"AI analysis failed: {exc}") from exc


def generate_structured_ai_response(
    user_query: str,
    quantitative_metrics: str,
    qualitative_insights: str,
    top_k_results: List[Dict[str, Any]],
) -> str:
    """Generate a structured Direct-Response Media Buyer analysis via RAG.

    Builds the full prompt using the structured template (via
    ``prompt_generator.generate_prompt``), then submits it to Gemini.
    The response is formatted as three markdown sections:
    Diagnostic Breakdown, Strategic Intervention, and Copy & Creative Rewrite.

    Parameters
    ----------
    user_query : str
        The raw question entered by the user.
    quantitative_metrics : str
        Pre-formatted per-campaign KPI block for selected campaigns.
    qualitative_insights : str
        Pre-formatted qualitative diagnostic observations.
    top_k_results : List[Dict[str, Any]]
        RAG-retrieved copywriting framework rules from the vector store.

    Returns
    -------
    str
        AI-generated structured markdown response.

    Raises
    ------
    ValueError
        If GEMINI_API_KEY is not set or user_query is empty.
    RuntimeError
        If google-genai is missing or the API call fails.
    """
    if not user_query or not user_query.strip():
        raise ValueError("user_query must be a non-empty string.")

    api_key: str = _get_api_key()

    try:
        from ai.prompt_generator import generate_prompt  # type: ignore
    except ImportError:
        from prompt_generator import generate_prompt  # type: ignore

    full_prompt: str = generate_prompt(
        user_query=user_query,
        quantitative_metrics=quantitative_metrics,
        qualitative_insights=qualitative_insights,
        top_k_results=top_k_results,
    )

    logger.info(
        "Initiating structured AI response | prompt=%d chars | rag_docs=%d",
        len(full_prompt),
        len(top_k_results),
    )

    client = _get_genai_client(api_key)

    try:
        response: Any = client.models.generate_content(
            model=_GEMINI_MODEL,
            contents=full_prompt,
            config={"max_output_tokens": _MAX_OUTPUT_TOKENS},
        )
        logger.info("Structured AI response generated successfully")
        return str(response.text)
    except Exception as exc:
        logger.error("Structured AI API call failed: %s", exc)
        raise RuntimeError(f"AI analysis failed: {exc}") from exc
