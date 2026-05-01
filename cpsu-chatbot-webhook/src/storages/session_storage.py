from src.connector.redis_connector import AsyncRedisConnector
import logging
import json


logger = logging.getLogger(__name__)

# ==================== Singleton SessionStorage ====================
_session_storage: "SessionStorage | None" = None


def get_session_storage() -> "SessionStorage":
    """Get singleton SessionStorage instance."""
    global _session_storage
    if _session_storage is None:
        _session_storage = SessionStorage()
    return _session_storage


class SessionStorage:
    """Async session storage using Redis."""
    
    TTL_SECONDS = 86400 # 1 Day
    
    def __init__(self):
        self.redis = AsyncRedisConnector().client

    def _get_key(self, user_id: str, platform: str) -> str:
        return f"session:{platform}:{user_id}"

    async def _get_data(self, key: str) -> dict:
        """Helper to get and parse JSON from Redis."""
        data = await self.redis.get(key)
        return json.loads(data) if data else {}

    async def _save_data(self, key: str, data: dict):
        """Helper to save JSON to Redis with TTL."""
        await self.redis.set(key, json.dumps(data), ex=self.TTL_SECONDS)

    async def set_session(self, user_id: str, platform: str, session_id: str) -> dict:
        """Create or update a session (session_id)."""
        key = self._get_key(user_id, platform)
        data = await self._get_data(key)
        
        data["session_id"] = session_id
        data["user_id"] = user_id
        data["platform"] = platform
        
        await self._save_data(key, data)
        return data

    async def get_session(self, user_id: str, platform: str) -> dict | None:
        """Get a session by user_id and platform and reset TTL."""
        key = self._get_key(user_id, platform)
        data = await self._get_data(key)
        if data:
            # Refresh TTL on read
            await self.redis.expire(key, self.TTL_SECONDS)
            return data
        return None

    async def set_processing(self, user_id: str, platform: str, processing: bool) -> dict:
        """Set processing status for a session."""
        key = self._get_key(user_id, platform)
        data = await self._get_data(key)
        
        data["processing"] = processing
        
        await self._save_data(key, data)
        return data

    async def push_message_queue(self, user_id: str, platform: str, message: str, reply_token: str | None = None) -> None:
        """Push message to queue (async)."""
        try:
            key = self._get_key(user_id, platform)
            data = await self._get_data(key)
            
            if "message_queue" not in data:
                 data["message_queue"] = []
                 
            data["message_queue"].append({
                 "text": message,
                 "reply_token": reply_token,
            })
            
            await self._save_data(key, data)
        except Exception as e:
            logger.exception(e)

    async def fetch_message_queue(self, user_id: str, platform: str) -> dict | None:
        """Fetch and clear message queue (async). Returns the data BEFORE clearing."""
        try:
            key = self._get_key(user_id, platform)
            data = await self._get_data(key)
            
            if not data or "message_queue" not in data or not data["message_queue"]:
                 return {"message_queue": []} # simulate empty

            # Deep copy to return
            old_data = json.loads(json.dumps(data))
            
            # Clear it
            data["message_queue"] = []
            await self._save_data(key, data)
            
            return old_data
            
        except Exception as e:
            logger.exception(e)
            return None