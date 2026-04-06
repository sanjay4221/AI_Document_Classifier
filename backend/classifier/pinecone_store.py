"""
pinecone_store.py — Pinecone Vector Storage (Future Similarity Search)
Currently stores classification results as embeddings for future use.

Future use cases:
- "Find documents similar to this invoice"
- "Show me all Finance docs from last month"
- Duplicate detection
- Classification improvement via similar document lookup

Currently: stubbed out — logs intent but does not block classification.
Enable fully when Pinecone API key is configured.
"""

from backend.core.config import settings
from backend.core.logger import logger


def store_classification(
    document_id: int,
    text: str,
    department: str,
    confidence: float,
) -> bool:
    """
    Store document embedding + classification metadata in Pinecone.
    Returns True if stored, False if skipped (no API key configured).
    """
    if not settings.PINECONE_API_KEY:
        logger.debug("Pinecone not configured — skipping vector storage")
        return False

    try:
        # TODO Phase 2: Enable when Pinecone is fully integrated
        # from pinecone import Pinecone
        # pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        # index = pc.Index(settings.PINECONE_INDEX)
        # embedding = _get_embedding(text)
        # index.upsert(vectors=[{
        #     "id": f"doc_{document_id}",
        #     "values": embedding,
        #     "metadata": {
        #         "document_id": document_id,
        #         "department": department,
        #         "confidence": confidence,
        #     }
        # }])
        logger.info(f"[Pinecone] Would store doc_{document_id} → {department}")
        return True

    except Exception as e:
        logger.warning(f"Pinecone storage failed (non-blocking): {e}")
        return False


def find_similar(text: str, department: str = None, top_k: int = 5) -> list:
    """
    Find similar previously classified documents.
    Returns empty list until Pinecone is fully enabled.
    """
    if not settings.PINECONE_API_KEY:
        return []

    # TODO Phase 2: Implement similarity search
    logger.debug("Pinecone similarity search not yet enabled")
    return []
