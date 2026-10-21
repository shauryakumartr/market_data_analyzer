import logging 
from typing import Any, Dict, List


logger : logging.Logger = logging.getLogger(__name__)

def generate_prompt(
        user_query: str,
        top_k_results: List[Dict[str,Any]]
) -> str : 
    
    prompt: str = "You are an elite direct-response media buyer and copywriter. " \
    "I will provide you with a failing ad, its diagnostic flags, and specific copywriting frameworks. " \
    "You must generate a structured and tailored response with high precision. Do not hallucinate or invent new rules. " \
    "Strictly apply the provided frameworks to rewrite the ad, and clearly explain exactly which rules were applied to fix the flagged issues."

    for result in top_k_results:
        content: str = result.get("content","")
        metadata: Dict[str, Any] = result.get("metadata", {})
        prompt += f"\n\nDocument Content: {content}\nMetadata: {metadata}"

    prompt += f"\n\nUser Query: {user_query}\n\nProvide a detailed and structured response based on the above information."

    
    