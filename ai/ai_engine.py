"""Module for interacting with the Google Gemini API to generate insights.

Sends structured analytics summaries and natural language prompts to Google Gemini AI models
to produce executive marketing consultation insights.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

# Module-level logger for Gemini AI engine operations
logger: logging.Logger = logging.getLogger(__name__)


def generate_ai_response(prompt: str, summary: Dict[str, Any]) -> str:
    """Generate an AI-powered marketing analysis response using Google Gemini API.

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
    api_key: Optional[str] = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set")
        raise ValueError(
            'GEMINI_API_KEY environment variable is not set. '
            'Please configure it in your environment or settings.'
        )

    logger.info("Initiating AI response generation for prompt length %d chars", len(prompt))

    try:
        from google import genai
        
        # Serialize the summary structure for content input
        summary_str: str = json.dumps(str(summary))
        client = genai.Client(api_key=api_key)
        
        response: Any = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=(
                f'Act as a business consultant. Answer the following question '
                f'based ONLY on the provided data. Do not invent or modify data.\n\n'
                f'DATA:\n{summary_str}\n\n'
                f'QUESTION: {prompt}\n\n'
                f'Write at least 200 to 300 words.'
            ),
            config={"max_output_tokens": 500}
        )
        logger.info("AI response generated successfully")
        return str(response.text)
    except ImportError:
        logger.error("google-genai package is not installed in the python environment")
        raise RuntimeError(
            'The google-genai package is required for AI features. '
            'Install it via pip: pip install google-genai'
        )
    except Exception as exc:
        logger.error("AI API call failed: %s", exc)
        raise RuntimeError(f"AI analysis failed: {exc}") from exc
