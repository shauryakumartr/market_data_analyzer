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

def embed_document_chunks(chunks: Dict[str, str]) -> List[Any]:
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
        if not content or not content.strip():
            logger.warning(f"Chunk '{title}' is empty. Skipping.")
            continue
            
        logger.debug(f"Generating embedding for chunk: '{title}'")
        
        try:
            results = client.models.embed_content(
                model="gemini-embedding-2",
                contents=content,
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
