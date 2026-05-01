from langchain_redis import RedisSemanticCache
from langchain_core.outputs import Generation
# from langsmith import traceable
from settings import Settings as ENV
from src.config.llm_factory import get_embeddings
import json
import logging


logger = logging.getLogger(__name__)

# ==================== Singleton SemanticCacheService ====================
_cache_service: "SemanticCacheService | None" = None


def get_semantic_cache_service() -> "SemanticCacheService":
    """Get singleton SemanticCacheService instance."""
    global _cache_service
    if _cache_service is None:
        _cache_service = SemanticCacheService()
    return _cache_service


class SemanticCacheService:
    """Semantic cache for RAG retrieval results using Redis Stack + langchain-redis.
    
    Maps retrieval queries to cached results using vector similarity.
    Uses RedisSemanticCache internally:
      - prompt    = user's search query
      - llm_string = "<index_name>:<serialized_filter>" (cache key namespace)
      - Generation.text = JSON-serialized retrieved docs
    """

    def __init__(self):
        self.embeddings = get_embeddings()
        self.distance_threshold = ENV.SEMANTIC_CACHE_THRESHOLD
        self.ttl = ENV.SEMANTIC_CACHE_TTL

        try:
            self.cache = RedisSemanticCache(
                redis_url=ENV.REDIS_URL,
                embeddings=self.embeddings,
                distance_threshold=self.distance_threshold,
                ttl=self.ttl,
                name="rag_semantic_cache"
            )
        except Exception as e:
            logger.error(f"Failed to initialize RedisSemanticCache: {e}")
            self.cache = None


    def _build_cache_key(self, index_name: str, filter: dict = None) -> str:
        """Build a unique cache key from index_name + filter."""
        if filter:
            filter_str = json.dumps(filter, sort_keys=True)
            return f"{index_name}:{filter_str}"
        return index_name
    

    # @traceable(name="cache_lookup")
    async def check_cache(self, query: str, index_name: str, filter: dict = None) -> list | None:
        """Check cache for semantically similar query.
        
        Args:
            query: The user's search query text
            index_name: Qdrant collection name (e.g. "academic", "staff")
            filter: Optional metadata filter dict
            
        Returns:
            List of cached retrieved docs if cache hit, None if miss
        """
        if not self.cache:
            return None

        cache_key = self._build_cache_key(index_name, filter)
        
        try:
            result = await self.cache.alookup(prompt=query, llm_string=cache_key)
            
            if result:
                # result is a list of Generation objects
                cached_text = result[0].text
                docs = json.loads(cached_text)
                logger.info(f"[Cache Lookup] Cache HIT for '{query[:50]}...' in [{index_name}] ({len(docs)} docs)")
                return docs
            
            logger.info(f"[Cache Lookup] Cache MISS for '{query[:50]}...' in [{index_name}]")
            
        except Exception as e:
            logger.error(f"[Cache Lookup Error] {e}")
        
        return None


    # @traceable(name="cache_save")
    async def save_to_cache(self, query: str, index_name: str, retrieved_docs: list, filter: dict = None):
        """Save retrieval results to semantic cache.
        
        Args:
            query: The user's search query text
            index_name: Qdrant collection name
            retrieved_docs: List of retrieved document dicts
            filter: Optional metadata filter dict
        """
        if not self.cache or not retrieved_docs:
            return

        cache_key = self._build_cache_key(index_name, filter)
        
        try:
            # Serialize docs as JSON and wrap in a Generation object
            docs_json = json.dumps(retrieved_docs, ensure_ascii=False)
            generation = Generation(text=docs_json)
            
            await self.cache.aupdate(
                prompt=query,
                llm_string=cache_key,
                return_val=[generation]
            )
            logger.info(f"[Cache Save] Cache SAVED for '{query[:50]}...' in [{index_name}]")
            
        except Exception as e:
            logger.error(f"[Cache Save Error] {e}")


    async def clear_cache(self):
        """Clear all cached entries."""
        if not self.cache:
            return
            
        try:
            await self.cache.aclear()
            logger.info("[Cache Clear] Semantic cache cleared")
        except Exception as e:
            logger.error(f"[Cache Clear Error] {e}")