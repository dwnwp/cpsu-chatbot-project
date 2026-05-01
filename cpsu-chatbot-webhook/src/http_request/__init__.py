import httpx
import logging


# ==================== Async HTTP Client ====================
_http_client: httpx.AsyncClient | None = None

logger = logging.getLogger(__name__)


def get_http_client() -> httpx.AsyncClient:
    """Get singleton async HTTP client with connection pooling."""
    global _http_client
    if _http_client is None:
        _http_client = httpx.AsyncClient(timeout=30.0)
        logger.info("[HTTP_CLIENT] Async HTTP client initialized")
    return _http_client


async def close_http_client():
    """Close HTTP client on shutdown."""
    global _http_client
    if _http_client is not None:
        await _http_client.aclose()
        _http_client = None
        logger.info("[HTTP_CLIENT] HTTP client closed")