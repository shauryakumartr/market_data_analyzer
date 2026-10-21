import logging
from pathlib import Path
from typing import Any, Dict, List

import chromadb

logger: logging.Logger = logging.getLogger(__name__)


_DEFAULT_DB_PATH: str = str(Path(__file__).resolve().parent.parent / "assets" / "vector_store")
_COLLECTION_NAME: str = "knowledge_base"


def top_k(
    query_embeddings: List[float],
    k: int = 5,
    db_path: str = _DEFAULT_DB_PATH,
) -> List[Dict[str, Any]]:
    """
    Queries the ChromaDB vector store and returns the top-k most similar documents
    to the supplied query embedding.

    Args:
        query_embeddings (List[float]): The embedding vector produced for the user query.
        k (int): Number of top results to return. Must be a positive integer. Defaults to 5.
        db_path (str): Path to the persistent ChromaDB storage directory.

    Returns:
        List[Dict[str, Any]]: A list of result dicts, each containing:
            - "id"       (str)  : ChromaDB document id.
            - "content"  (str)  : The stored document text.
            - "metadata" (dict) : Associated metadata (title, source, etc.).
            - "distance" (float): Inner-product distance to the query vector.

    Raises:
        TypeError:  If ``query_embeddings`` is not a list, or ``k`` is not an integer.
        ValueError: If ``query_embeddings`` is empty, or ``k`` is not a positive integer.
        RuntimeError: If the ChromaDB client/collection cannot be initialised or the
                      query itself fails.
    """
    # ------------------------------------------------------------------ #
    #  Input validation                                                    #
    # ------------------------------------------------------------------ #
    if not isinstance(query_embeddings, list):
        logger.error(
            f"query_embeddings must be a list of floats, got {type(query_embeddings).__name__}."
        )
        raise TypeError(
            f"query_embeddings must be a list of floats, got {type(query_embeddings).__name__}."
        )

    if not query_embeddings:
        logger.error("query_embeddings is empty. Cannot perform similarity search.")
        raise ValueError("query_embeddings must be a non-empty list of floats.")

    if not isinstance(k, int):
        logger.error(f"k must be an integer, got {type(k).__name__}.")
        raise TypeError(f"k must be an integer, got {type(k).__name__}.")

    if k <= 0:
        logger.error(f"k must be a positive integer, got {k}.")
        raise ValueError(f"k must be a positive integer, got {k}.")

    # ------------------------------------------------------------------ #
    #  ChromaDB client & collection                                        #
    # ------------------------------------------------------------------ #
    logger.debug(f"Connecting to ChromaDB at '{db_path}'.")
    try:
        client = chromadb.PersistentClient(path=db_path)
    except Exception as e:
        logger.error(f"Failed to initialise ChromaDB client at '{db_path}': {e}")
        raise RuntimeError(f"Failed to initialise ChromaDB client: {e}") from e

    try:
        collection = client.get_or_create_collection(
            name=_COLLECTION_NAME,
            metadata={"hnsw:space": "ip"},
        )
        logger.debug(f"Connected to collection '{_COLLECTION_NAME}'.")
    except Exception as e:
        logger.error(f"Failed to get or create collection '{_COLLECTION_NAME}': {e}")
        raise RuntimeError(f"Failed to access ChromaDB collection: {e}") from e

    # ------------------------------------------------------------------ #
    #  Query                                                               #
    # ------------------------------------------------------------------ #
    logger.info(f"Querying ChromaDB for top {k} results.")
    try:
        results = collection.query(
            query_embeddings=[query_embeddings],
            n_results=k,
        )
    except Exception as e:
        logger.error(f"ChromaDB query failed: {e}")
        raise RuntimeError(f"ChromaDB query failed: {e}") from e

    # ------------------------------------------------------------------ #
    #  Guard: ensure expected keys exist in the response                   #
    # ------------------------------------------------------------------ #
    required_keys = ("ids", "documents", "metadatas", "distances")
    for key in required_keys:
        if key not in results or not results[key]:
            logger.error(
                f"ChromaDB response is missing or has empty field '{key}'. "
                f"Available keys: {list(results.keys())}"
            )
            raise RuntimeError(
                f"Unexpected ChromaDB response structure — missing field '{key}'."
            )

    query_ids: List[str] = results["ids"][0]
    query_docs: List[str] = results["documents"][0]
    query_metas: List[Dict[str, Any]] = results["metadatas"][0]
    query_dists: List[float] = results["distances"][0]

    # Sanity-check: all four lists must have the same length
    lengths = {len(query_ids), len(query_docs), len(query_metas), len(query_dists)}
    if len(lengths) != 1:
        logger.error(
            f"ChromaDB returned misaligned result lists: "
            f"ids={len(query_ids)}, docs={len(query_docs)}, "
            f"metas={len(query_metas)}, dists={len(query_dists)}."
        )
        raise RuntimeError("ChromaDB response lists are not aligned in length.")

    # ------------------------------------------------------------------ #
    #  Build result list                                                   #
    # ------------------------------------------------------------------ #
    top_k_results: List[Dict[str, Any]] = []

    for i in range(len(query_ids)):
        if query_dists[i] is None or query_docs[i] is None or query_metas[i] is None:
            logger.warning(
                f"Skipping result at index {i} (id={query_ids[i]}) due to missing data."
            )
            continue

        top_k_results.append(
            {
                "id": query_ids[i],
                "content": query_docs[i],
                "metadata": query_metas[i],
                "distance": query_dists[i],
            }
        )

    logger.info(
        f"Returning {len(top_k_results)} result(s) "
        f"(skipped {len(query_ids) - len(top_k_results)} incomplete record(s))."
    )
    return top_k_results
