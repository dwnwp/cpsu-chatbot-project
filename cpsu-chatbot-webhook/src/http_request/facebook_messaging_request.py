from src.http_request import get_http_client
from settings import Settings as ENV
import asyncio
import httpx
import logging

logger = logging.getLogger(__name__)


# ==================== Facebook API Helper ====================
async def _send_facebook_api(url: str, payload: dict, params: dict, max_retries: int = 3):
    """Send request to Facebook API with retry and exponential backoff."""

    client = get_http_client()

    for attempt in range(max_retries):
        try:
            res = await client.post(url, params=params, json=payload)
            res.raise_for_status()
            return res
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500 and attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 0.5
                logger.warning(f"[FACEBOOK] API error {e.response.status_code}, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise
        except httpx.RequestError:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) * 0.5
                logger.warning(f"[FACEBOOK] API request error, retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise


async def reply_text_facebook(uid: str, text: str):
    """Send text message to Facebook (async with retry)."""

    params = {"access_token": ENV.FACEBOOK_TOKEN}
    payload = {
        "recipient": {"id": uid},
        "messaging_type": "RESPONSE",
        "message": {"text": text},
    }
    url = f"https://graph.facebook.com/v25.0/{ENV.FACEBOOK_PAGE_ID}/messages"
    await _send_facebook_api(url, payload, params)


async def reply_image_facebook(uid: str, image_url_list: list[str]):
    """Send image messages to Facebook (async with retry)."""

    params = {"access_token": ENV.FACEBOOK_TOKEN}
    for image_url in image_url_list:
        payload = {
            "recipient": {"id": uid},
            "messaging_type": "RESPONSE",
            "message": {
                "attachment": {
                    "type": "image",
                    "payload": {"url": image_url, "is_reusable": True},
                }
            },
        }
        url = f"https://graph.facebook.com/v25.0/{ENV.FACEBOOK_PAGE_ID}/messages"
        await _send_facebook_api(url, payload, params)


async def show_typing_animation_facebook(uid: str):
    """Show typing animation to Facebook (async with retry)."""

    params = {"access_token": ENV.FACEBOOK_TOKEN}
    payload = {
        "recipient": {"id": uid},
        "sender_action": "typing_on",
    }
    url = f"https://graph.facebook.com/v25.0/{ENV.FACEBOOK_PAGE_ID}/messages"
    await _send_facebook_api(url, payload, params)