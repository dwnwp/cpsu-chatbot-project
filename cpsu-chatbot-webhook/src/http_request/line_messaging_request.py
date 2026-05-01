from src.http_request import get_http_client
import uuid


LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"


def chunk_list(data: list, size: int):
    for i in range(0, len(data), size):
        yield data[i:i + size]


def build_image_messages(image_urls: list[str]) -> list[dict]:
    messages = []

    for url in image_urls:
        messages.append({
            "type": "image",
            "originalContentUrl": url,
            "previewImageUrl": url
        })

    return messages


async def push_line_images(channel_access_token: str, user_id: str, image_urls: list[str]):
    client = get_http_client()

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {channel_access_token}"
    }

    results = []

    for batch in chunk_list(image_urls, 5):

        messages = build_image_messages(batch)

        payload = {
            "to": user_id,
            "messages": messages
        }

        headers["X-Line-Retry-Key"] = str(uuid.uuid4())

        response = await client.post(
            url=LINE_PUSH_URL,
            headers=headers,
            json=payload,
            timeout=10
        )

        results.append({
            "status": response.status_code,
            "response": response.text
        })

    response.raise_for_status()

    return results