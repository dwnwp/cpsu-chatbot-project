import redis.asyncio as redis
from settings import Settings as ENV
import logging

logger = logging.getLogger(__name__)

class AsyncRedisConnector:
    """Async Redis connector using connection pooling."""
    
    _pool: redis.ConnectionPool | None = None
    
    @classmethod
    def get_pool(cls) -> redis.ConnectionPool:
        if cls._pool is None:
            logger.info("Redis connection initialized")
            cls._pool = redis.ConnectionPool.from_url(
                ENV.REDIS_URL,
                decode_responses=True # Returns strings instead of bytes
            )
        return cls._pool

    def __init__(self):
        self.client = redis.Redis(connection_pool=self.get_pool())

    async def ping(self) -> bool:
        """Test the connection."""
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def close(self):
        """Close the connection pool. Usually not needed for individual clients if pooling."""
        if self._pool:
            await self._pool.disconnect()
            AsyncRedisConnector._pool = None
            logger.info("Redis connection pool disconnected")
