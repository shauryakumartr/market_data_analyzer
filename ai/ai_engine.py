"""Module for interacting with the Google Gemini API to generate insights.
"""

import os
import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

def generate_ai_response(prompt: str, summary: dict[str, Any]) -> str:
    """Generate an AI-powered marketing analysis response.

    Uses the Google Gemini API to answer user questions based on campaign analytics data.

    Parameters
    ----------
    prompt : str
        User's question.
    summary : dict
        Compiled analytics summary for context.

    Returns
    -------
    str
        AI-generated response text.
    """
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set")
        raise ValueError(
            'GEMINI_API_KEY environment variable is not set. '
            'Please configure it in your environment or setting.'
        )

    logger.info("Generating AI response. Prompt length: %d", len(prompt))

    try:
        from google import genai
        
        # Serialize the summary structure for content input
        summary_str = json.dumps(str(summary))
        client = genai.Client(api_key=api_key)
        
        response = client.models.generate_content(
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
        return response.text
    except ImportError:
        logger.error("google-genai package is not installed")
        raise RuntimeError(
            'The google-genai package is required for AI features. '
            'Install it via pip: pip install google-genai'
        )
    except Exception as exc:
        logger.error("AI API call failed: %s", exc)
        raise RuntimeError(f"AI analysis failed: {exc}") from exc

