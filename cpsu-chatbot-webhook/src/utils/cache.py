import time
import logging
from collections import OrderedDict

logger = logging.getLogger(__name__)


class TTLOrderedDict:
    """OrderedDict with TTL and max size to prevent memory leaks."""

    def __init__(self, max_size: int = 10000, ttl_seconds: int = 3600):
        self._data: OrderedDict = OrderedDict()
        self._max_size = max_size
        self._ttl = ttl_seconds

    def add(self, key: str, value: float = None):
        """Add a key with current timestamp."""
        self._cleanup()
        self._data[key] = value if value is not None else time.time()
        # Limit size
        while len(self._data) > self._max_size:
            self._data.popitem(last=False)

    def get(self, key: str) -> float | None:
        """Get value if exists and not expired."""
        if key not in self._data:
            return None
        if time.time() - self._data[key] > self._ttl:
            self._data.pop(key, None)
            return None
        return self._data[key]

    def __contains__(self, key: str) -> bool:
        """Check if key exists and not expired."""
        return self.get(key) is not None

    def increment(self, key: str) -> int:
        """Increment counter for key, return new count."""
        # For rate limiting: value is (count, first_request_time)
        now = time.time()
        if key in self._data:
            count, first_time = self._data[key]
            if now - first_time > self._ttl:
                # Window expired, reset
                self._data[key] = (1, now)
                return 1
            else:
                self._data[key] = (count + 1, first_time)
                return count + 1
        else:
            self._data[key] = (1, now)
            return 1

    def _cleanup(self):
        """Remove expired entries."""
        now = time.time()
        expired = []
        for k, v in self._data.items():
            if isinstance(v, tuple):
                if now - v[1] > self._ttl:
                    expired.append(k)
            elif isinstance(v, (int, float)):
                if now - v > self._ttl:
                    expired.append(k)
        for k in expired:
            self._data.pop(k, None)


class RateLimiter:
    """Simple per-user rate limiter."""

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        self._data: OrderedDict = OrderedDict()
        self._max_requests = max_requests
        self._window = window_seconds

    def check(self, user_id: str) -> bool:
        """Check if user is allowed. Returns True if allowed."""
        now = time.time()

        if user_id in self._data:
            count, first_time = self._data[user_id]
            if now - first_time > self._window:
                self._data[user_id] = (1, now)
                return True
            elif count >= self._max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False
            else:
                self._data[user_id] = (count + 1, first_time)
                return True
        else:
            self._data[user_id] = (1, now)
            return True


class AsyncRateLimiter:
    """Redis-backed per-user rate limiter using fixed-window counter.
    
    Uses a Lua script for atomic INCR + EXPIRE to prevent race conditions.
    Works correctly across multiple process replicas.
    Fails open (allows request) if Redis is temporarily unavailable.
    """

    _RATE_LIMIT_SCRIPT = """
    local count = redis.call('INCR', KEYS[1])
    if count == 1 then
        redis.call('EXPIRE', KEYS[1], ARGV[1])
    end
    return count
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 60):
        from src.connector.redis_connector import AsyncRedisConnector
        self.redis = AsyncRedisConnector().client
        self.max_requests = max_requests
        self.window = window_seconds
        self._script = self.redis.register_script(self._RATE_LIMIT_SCRIPT)

    async def check(self, user_id: str) -> bool:
        """Check if user is allowed. Returns True if allowed."""
        key = f"ratelimit:{user_id}"
        try:
            count = await self._script(keys=[key], args=[self.window])
            if count > self.max_requests:
                logger.warning(f"Rate limit exceeded for user {user_id}")
                return False
            return True
        except Exception as e:
            logger.error(f"Rate limiter Redis error: {e}")
            return True  # Fail open — allow request if Redis is down

