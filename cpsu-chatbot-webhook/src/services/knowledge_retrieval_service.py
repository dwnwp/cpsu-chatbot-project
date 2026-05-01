from qdrant_client import AsyncQdrantClient, models
# from langsmith import traceable
from typing import List
from src.services.semantic_cache_service import get_semantic_cache_service
from src.config.llm_factory import get_llm, get_embeddings
from src.prompts import load_prompt
from settings import Settings as ENV
import asyncio
import logging


logger = logging.getLogger(__name__)

# ==================== Singleton RetrievalService ====================
_retrieval_service: "RetrievalService | None" = None


def get_retrieval_service() -> "RetrievalService":
    """Get singleton RetrievalService instance."""
    global _retrieval_service
    if _retrieval_service is None:
        _retrieval_service = RetrievalService()
        logger.info("Qdrant connection initialized")
    return _retrieval_service


class RetrievalService:
    """Async RAG retrieval service using Vector Similarity."""
    
    def __init__(self):
        self.llm = get_llm(model_name=ENV.LLM_MODEL_NAME, temperature=0.7)
        self.embeddings = get_embeddings()
        self.qdrant_client = AsyncQdrantClient(
            host=ENV.QDRANT_HOST,
            grpc_port=ENV.QDRANT_PORT,
            prefer_grpc=True,
            timeout=10.0
        )
        self.cache_service = get_semantic_cache_service()
        self.SAVE_TO_CACHE_THRESHOLD = 0.60


    # @traceable(name="generate_multi_queries")
    async def _generate_multi_queries(self, original_query: str) -> List[str]:
        """Generate multiple query variations (async — non-blocking)."""
        try:
            prompt_template = load_prompt("multi_query_generator")
            response = await self.llm.ainvoke(f"{prompt_template}\n\nQuery: {original_query}")
            content = response.content
            queries = [line.strip() for line in content.split('\n') if line.strip()]
            return list(set(queries))
        except Exception as e:
            logger.error(f"Error generating queries: {e}")
            return [original_query]


    # @traceable(name="get_embedding")
    async def _get_embedding(self, input: List[str]) -> List[List[float]]:
        """Get embeddings (async — non-blocking)."""
        try:
            inputs = [q.replace("\n", " ") for q in input]
            return await self.embeddings.aembed_documents(inputs)
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []


    async def _search_qdrant_async(self, collection_name: str, vector: List[float], filter: dict, top_k: int) -> list:
        """Search Qdrant asynchronously using native gRPC API."""
        
        qdrant_filter = None
        if filter:
            conditions = []
            for key, val in filter.items():
                if isinstance(val, dict) and "$eq" in val:
                    conditions.append(models.FieldCondition(key=key, match=models.MatchValue(value=val["$eq"])))
                elif isinstance(val, str):
                    conditions.append(models.FieldCondition(key=key, match=models.MatchValue(value=val)))
            if conditions:
                qdrant_filter = models.Filter(must=conditions)

        return await self.qdrant_client.search(
            collection_name=collection_name,
            query_vector=vector,
            query_filter=qdrant_filter,
            limit=top_k,
            with_payload=True
        )


    # @traceable(name="retrieve_multi_query")
    async def retrieve_multi_query(self, query: str, user_question: str, index_name: str, filter: dict = None, top_k: int = 5):
        """Retrieve documents using multi-query approach (async)."""

        cached_docs = await self.cache_service.check_cache(
            query=query,
            index_name=index_name,
            filter=filter
        )
        if cached_docs:
            return cached_docs
        
        # Run Multi-Query Retrieval
        query_vectors = await self._get_embedding([query, user_question])
        if not query_vectors:
            return []

        # generated_queries = await self._generate_multi_queries(query)
        # logger.info(f"Generated {len(generated_queries)} queries")
    
        # Batch embedding (single API call)
        # generated_vectors = await self._get_embedding(generated_queries)
        # all_vectors = generated_vectors + query_vectors

        # Run all Qdrant queries concurrently using asyncio.gather
        search_tasks = [
            self._search_qdrant_async(index_name, vector, filter, top_k)
            for vector in query_vectors
        ]
        
        results_list = await asyncio.gather(*search_tasks, return_exceptions=True)

        # Merge and deduplicate results
        all_matches = {}
        for results in results_list:
            if isinstance(results, Exception):
                logger.error(f"[Qdrant] Qdrant query failed: {results}")
                continue
                
            for match in results:
                if match.score < 0.5 and index_name != "staff":
                    continue

                doc_id = str(match.id)
                if doc_id not in all_matches or match.score > all_matches[doc_id]['score']:
                    all_matches[doc_id] = {
                        "score": match.score,
                        "content": match.payload.get('text', ''),
                        "metadata": match.payload
                    }

        # Sort by score and limit
        sorted_matches = sorted(all_matches.values(), key=lambda x: x['score'], reverse=True)
        final_results = sorted_matches[:top_k]

        if final_results:
            best_score = final_results[0]['score']
            if best_score >= self.SAVE_TO_CACHE_THRESHOLD:
                await self.cache_service.save_to_cache(
                    query=query,
                    index_name=index_name,
                    retrieved_docs=final_results,
                    filter=filter
                )
            else:
                logger.info(f"Score too low for cache: {best_score:.4f}")

        return final_results