"""
Hindsight memory client wrapper.
Uses hindsight-client SDK with bank_id scoping.
Banks are created lazily on first retain call.
"""
import logging
from hindsight_client import Hindsight
from backend.config import settings

logger = logging.getLogger(__name__)

_client: Hindsight | None = None


def get_client() -> Hindsight:
    global _client
    if _client is None:
        _client = Hindsight(
            base_url="https://api.hindsight.vectorize.io",
            api_key=settings.hindsight_api_key,
        )
    return _client


def retain(content: str, metadata: dict | None = None) -> dict:
    """Store a resolved incident in Hindsight memory."""
    client = get_client()
    try:
        result = client.retain(
            bank_id=settings.hindsight_bank_id,
            content=content,
        )
        logger.info("Retained memory: %s...", content[:80])
        return result or {}
    except Exception as e:
        logger.error("Hindsight retain failed: %s", e)
        return {}


def recall(query: str, top_k: int = 5) -> list[dict]:
    """Recall semantically similar past incidents from memory."""
    client = get_client()
    try:
        response = client.recall(
            bank_id=settings.hindsight_bank_id,
            query=query,
        )
        results = []
        if hasattr(response, "results"):
            for r in response.results[:top_k]:
                text = getattr(r, "text", None) or str(r)
                # scores is a RecallScores object; extract composite or first numeric field
                scores_obj = getattr(r, "scores", None)
                score = None
                if scores_obj is not None:
                    score = (
                        getattr(scores_obj, "composite", None)
                        or getattr(scores_obj, "semantic", None)
                        or getattr(scores_obj, "relevance", None)
                    )
                results.append({"text": text, "score": score})
        logger.info("Recalled %d results for query: %s...", len(results), query[:60])
        return results
    except Exception as e:
        logger.error("Hindsight recall failed: %s", e)
        return []
