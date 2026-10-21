import logging
from pathlib import Path
from typing import Dict, Any, Optional, List
import chromadb

# Resolved relative to this file's location: ai/ -> project root -> assets/vector_store
# Works on any machine regardless of where the project is cloned.
_DEFAULT_DB_PATH: str = str(Path(__file__).resolve().parent.parent / "assets" / "vector_store")

try:
    from ai.chunker import generate_chunks
    from ai.embedder import embed_document_chunks
except ImportError:
    from chunker import generate_chunks
    from embedder import embed_document_chunks

logger = logging.getLogger(__name__)

def _create_vector_store(path: str = _DEFAULT_DB_PATH) -> Any:
    """
    Initializes and returns a persistent ChromaDB collection.
    
    Args:
        path (str): The directory path for the persistent ChromaDB storage.
        
    Returns:
        Any: The ChromaDB collection object.
    """
    try:
        client = chromadb.PersistentClient(path=path)
        collection = client.get_or_create_collection(name="knowledge_base", metadata={"hnsw:space": "ip"})
        logger.info(f"Successfully connected to vector store at {path}")
        return collection
    except Exception as e:
        logger.error(f"Failed to create or retrieve vector store collection: {e}")
        raise

def add_documents_to_vector_store(chunks: Optional[Dict[str, Any]] = None) -> None:
    """
    Processes document chunks, generates embeddings, and stores them in ChromaDB.
    
    Args:
        chunks (Optional[Dict[str, Any]]): A dictionary of chunks. If None, it will be generated.
    """
    try:
        collection = _create_vector_store()
    except Exception:
        logger.error("Aborting document addition due to vector store initialization failure.")
        return

    # Original workflow generated chunks internally, safety net added to reuse passed arguments
    if not chunks:
        try:
            chunks = generate_chunks()
        except Exception as e:
            logger.error(f"Failed to generate chunks: {e}")
            return
            
    if not chunks:
        logger.warning("No chunks available to add to the vector store.")
        return

    try:
        embeddings = embed_document_chunks(chunks)
    except Exception as e:
        logger.error(f"Failed to generate embeddings: {e}")
        return

    if not embeddings:
        logger.warning("No embeddings returned. Aborting.")
        return

    # Safety net: Ensure 1:1 mapping between chunks and embeddings to prevent IndexErrors
    if len(embeddings) != len(chunks):
        logger.error(f"Mismatch: Received {len(chunks)} chunks but {len(embeddings)} embeddings. "
                     f"Cannot safely align data. Aborting.")
        return

    ids: List[str] = []
    embeddings_list: List[Any] = []
    metadatas: List[Dict[str, str]] = []
    documents: List[str] = []

    for i, (title, content) in enumerate(chunks.items()):
        try:
            ids.append(str(i))
            embeddings_list.append(embeddings[i])
            
            # Safety net: Gracefully handle if content is a dictionary (legacy) or a string
            if isinstance(content, dict):
                source = str(content.get("source", title))
                doc_text = str(content.get("content", ""))
            else:
                source = str(title)
                doc_text = str(content)
                
            metadatas.append({"title": str(title), "source": source})
            documents.append(doc_text)
            
        except Exception as e:
            logger.warning(f"Error processing chunk {i} ({title}): {e}. Skipping this chunk.")
            # Rollback the last additions to maintain array length alignment
            if len(ids) > len(documents):
                ids.pop()
                embeddings_list.pop()
            continue

    if not documents:
        logger.warning("No valid documents processed to add to ChromaDB.")
        return

    try:
        collection.add(
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings_list,
            ids=ids
        )
        logger.info(f"Successfully added {len(documents)} documents to the vector store.")
    except Exception as e:
        logger.error(f"Failed to add documents to ChromaDB collection: {e}")
