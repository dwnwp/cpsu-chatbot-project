from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from src.storages.session_storage import get_session_storage
from typing import Literal
import logging
import json


logger = logging.getLogger(__name__)

session_storage = get_session_storage()


def _get_history_key(user_id: str, platform: str) -> str:
    return f"chat_history:{platform}:{user_id}"


async def conversation_get_or_create(user_id: str, platform: Literal['facebook', 'line']) -> str:
    """Get existing or create new conversation (async). Returns user_id as a mock session_id."""
    try:
        session_id = f"session_{platform}_{user_id}"
        await session_storage.set_session(user_id, platform, session_id)
        
        # Ensure the history key is touched
        history_key = _get_history_key(user_id, platform)
        if not await session_storage.redis.exists(history_key):
             await session_storage.redis.set(history_key, "[]", ex=session_storage.TTL_SECONDS)
        else:
             await session_storage.redis.expire(history_key, session_storage.TTL_SECONDS)

        return session_id
    except Exception as e:
        logger.exception(e)
        raise


async def conversation_delete(user_id: str, platform: Literal['facebook', 'line']) -> bool:
    """Delete a conversation (async)."""
    try:
        history_key = _get_history_key(user_id, platform)
        result = await session_storage.redis.delete(history_key)
        return result > 0
    except Exception as e:
        logger.exception(e)
        return False


async def reset_conversation(user_id: str, platform: Literal['facebook', 'line']) -> str | None:
    """Reset conversation by deleting and creating new (async)."""
    try:
        if await conversation_delete(user_id, platform):
            await unlock_process_running(user_id, platform)
            return await conversation_get_or_create(user_id, platform)
        return None
    except Exception as e:
        logger.exception(e)
        return None


async def conversation_list_items(user_id: str, platform: str) -> list:
    """List conversation items from Redis."""
    try:
        history_key = _get_history_key(user_id, platform)
        data = await session_storage.redis.get(history_key)
        if data:
            return json.loads(data)
        return []
    except Exception as e:
        logger.warning(f"Could not list items for {user_id}: {e}")
        return []


def conversation_items_to_history(items: list) -> list[BaseMessage]:
    """Convert stored conversation items to LangChain message objects."""
    messages = []
    for item in items:
        role = item.get("role", "")
        content = item.get("content", "")
        if isinstance(content, list):
            content = " ".join(
                block.get("text", "") for block in content
                if isinstance(block, dict) and block.get("type") in ("text", "input_text")
            )
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))
    return messages


def _safe_serialize_item(item) -> dict | None:
    """Convert an item to a JSON-safe dict."""
    if isinstance(item, dict):
        return item
    # If it has a model_dump method (pydantic), use it
    if hasattr(item, "model_dump"):
        return item.model_dump()
    # If it has a to_dict method, use it
    if hasattr(item, "to_dict"):
        return item.to_dict()
    # Try converting via json round-trip
    try:
        return json.loads(json.dumps(item, default=str))
    except (TypeError, ValueError):
        logger.warning(f"Could not serialize item: {type(item)}")
        return None


async def conversation_create_item(user_id: str, platform: str, items: list[dict]):
    """Create conversation items (append to Redis history)."""
    try:
        history_key = _get_history_key(user_id, platform)
        current_data = await session_storage.redis.get(history_key)
        
        if current_data:
            history = json.loads(current_data)
        else:
            history = []
        
        for item in items:
            serialized = _safe_serialize_item(item)
            if serialized:
                history.append(serialized)
        
        await session_storage.redis.set(history_key, json.dumps(history, default=str), ex=session_storage.TTL_SECONDS)
    except Exception as e:
        logger.exception(e)


async def push_message_queue(user_id: str, platform: str, message: str, reply_token: str | None = None) -> None:
    """Push message to queue (async)."""
    await session_storage.push_message_queue(user_id, platform, message, reply_token)


async def fetch_message_queue(user_id: str, platform: str) -> dict | None:
    """Fetch and clear message queue (async). Returns the data BEFORE clearing."""
    return await session_storage.fetch_message_queue(user_id, platform)


async def lock_process_running(user_id: str, platform: str) -> bool:
    """Lock processing state (async). Returns True only if the lock was newly acquired."""
    try:
        lock_key = f"lock:{platform}:{user_id}"
        # SET NX: only sets if the key does NOT exist → returns True if lock acquired
        acquired = await session_storage.redis.set(
            lock_key, "1", nx=True, ex=session_storage.TTL_SECONDS
        )
        return acquired is not None
    except Exception as e:
        logger.exception(e)
        return False


async def unlock_process_running(user_id: str, platform: str) -> None:
    """Unlock processing state (async)."""
    try:
        lock_key = f"lock:{platform}:{user_id}"
        await session_storage.redis.delete(lock_key)
    except Exception as e:
        logger.exception(e)