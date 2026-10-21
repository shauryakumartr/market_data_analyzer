import os
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
from google import genai
from google.genai import types

try:
    from ai.chunker import generate_chunks
except ImportError:
    from chunker import generate_chunks

logger = logging.getLogger(__name__)

def embed_document_chunks(chunks: Dict[str, Dict[str, str]]) -> List[Any]:
    """
    Generates embeddings for document chunks using the Gemini API.
    
    Args:
        chunks (Dict[str, str]): A dictionary where keys are chunk titles/headings 
                                 and values are the text content.
        
    Returns:
        List[Any]: A list of generated embeddings.
    """
    if not chunks:
        logger.warning("No chunks provided for embedding. Returning empty list.")
        return []

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables.")
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    
    try:
        client = genai.Client(api_key=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize GenAI client: {e}")
        raise
        
    embeddings: List[Any] = []
    
    logger.info(f"Starting embedding generation for {len(chunks)} chunks.")

    for title, content in chunks.items():
        if not content["content"] or not content["content"].strip():
            logger.warning(f"Chunk '{title}' is empty. Skipping.")
            continue
            
        logger.debug(f"Generating embedding for chunk: '{title}'")
        
        try:
            results = client.models.embed_content(
                model="gemini-embedding-2",
                contents=content["content"],
                config=types.EmbedContentConfig(
                    task_type="RETRIEVAL_DOCUMENT",
                    title=title
                )
            )
            embeddings.append(results.embeddings)
        except Exception as e:
            logger.error(f"Error generating embedding for chunk '{title}': {e}")
            continue

    logger.info(f"Successfully generated {len(embeddings)} embeddings.")
    return embeddings


def embed_query(query: str) -> List[float]:
    """
    Generates an embedding for a user query using the Gemini API for similarity comparison.

    Uses the RETRIEVAL_QUERY task type, which produces embeddings optimised for
    comparing against document embeddings generated with RETRIEVAL_DOCUMENT.

    Args:
        query (str): The raw user query string to embed.

    Returns:
        List[float]: A flat list of floats representing the query embedding vector.

    Raises:
        ValueError: If the query is empty or the API key is missing.
        RuntimeError: If the GenAI client cannot be initialised or the API call fails.
    """
    if not query or not query.strip():
        logger.error("embed_query received an empty or whitespace-only query.")
        raise ValueError("Query must be a non-empty string.")

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment variables.")
        raise ValueError("GEMINI_API_KEY not found in environment variables.")

    try:
        client = genai.Client(api_key=api_key)
        logger.debug("GenAI client initialised successfully for query embedding.")
    except Exception as e:
        logger.error(f"Failed to initialise GenAI client: {e}")
        raise RuntimeError(f"Failed to initialise GenAI client: {e}") from e

    logger.info(f"Generating embedding for query: '{query[:80]}{'...' if len(query) > 80 else ''}'")

    try:
        results = client.models.embed_content(
            model="gemini-embedding-2",
            contents=query.strip(),
            config=types.EmbedContentConfig(
                task_type="RETRIEVAL_QUERY",
                title="query"
            )
        )
    except Exception as e:
        logger.error(f"Gemini API call failed while embedding query: {e}")
        raise RuntimeError(f"Failed to generate query embedding: {e}") from e

    if not results or not results.embeddings:
        logger.error("Gemini API returned no embeddings for the query.")
        raise RuntimeError("No embedding returned for the query.")

    logger.info("Query embedding generated successfully.")
    return results.embeddings


