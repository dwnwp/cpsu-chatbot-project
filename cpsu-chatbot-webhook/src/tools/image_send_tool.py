from langchain_core.tools import tool
from langchain_core.runnables.config import RunnableConfig
from src.connector.minio_connector import MinioConnector
from src.http_request import line_messaging_request
from src.http_request.facebook_messaging_request import reply_image_facebook
from settings import Settings as ENV
from src.utils.encode_url_list import encode_urls
import logging

connector = MinioConnector()
logger = logging.getLogger(__name__)


async def send_images(platform: str, user_id: str, image_urls: list[str], config: RunnableConfig | None = None):

  encoded_urls = encode_urls(image_urls)

  if config is not None:
    metadata = config.get("metadata", {})
    pending = metadata.setdefault("pending_images", [])
    pending.extend(encoded_urls)
  else:
    # Fallback if no config is provided (shouldn't happen in normal flow)
    if platform == "line":
      await line_messaging_request.push_line_images(
        channel_access_token=ENV.LINE_CHANNEL_ACCESS_TOKEN,
        user_id=user_id,
        image_urls=encoded_urls
      )
    elif platform == "facebook":
      await reply_image_facebook(user_id, encoded_urls)


@tool
async def send_office_hours_image(config: RunnableConfig) -> str:
  """Send office hours image to the user. Call this when user asks about office hours or working times."""
  logger.info("send_office_hours_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/office_hours/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent office hours image to the user. [NEXT_ACTION] Respond to the user 'ดูรูปภาพเพิ่มเติมได้เลยน้าา'."

  except Exception as e:
    logger.error(f"Error sending office hours image: {e}")
    return "Failed to send office hours image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize."


@tool
async def send_su_map_image(config: RunnableConfig) -> str:
  """Send university map image to the user. Call this when user asks about campus map or locations."""
  logger.info("send_su_map_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/map_SU/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent university map image to the user. [NEXT_ACTION] Respond to the user 'ดูรูปภาพเพิ่มเติมได้เลยน้าา'."

  except Exception as e:
    logger.error(f"Error sending SU map image: {e}")
    return "Failed to send map image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize."


@tool
async def send_academic_staff_image(name: str, config: RunnableConfig) -> str:
  """Send academic staff photo. Call this when staff_search_tool is triggered.
  
  Args:
  - name: The name of the staff member
  """
  logger.info("send_academic_staff_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    bucket_name = connector.bucket_name
    search_name = name.strip()
    prefix = "images/academic_staff/"
    objects = connector.client.list_objects(bucket_name, prefix=prefix, recursive=True)

    matched_urls = []

    for obj in objects:
      if search_name in obj.object_name and obj.object_name.lower().endswith(('.jpg', '.png', '.jpeg')):
        url = connector.get_public_url(obj.object_name)
        matched_urls.append(url)

    await send_images(platform, user_id, matched_urls, config)

    return "Successfully sent academic staff photo to the user. [NEXT_ACTION] Now respond to the user with the staff information you already retrieved."

  except Exception as e:
    logger.error(f"Error sending academic staff image: {e}")
    return "Failed to send academic staff image. [NEXT_ACTION] Inform the user that the photo could not be sent and apologize. Still respond with the staff information you already retrieved."


@tool
async def send_calendar_image(config: RunnableConfig) -> str:
  """Send academic calendar image to the user. Call this when user asks about dates."""
  logger.info("send_calendar_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/calendar/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent academic calendar image to the user. [NEXT_ACTION] You MUST now call 'academic_search_tool()' to retrieve the exact date information relevant to the user's question."

  except Exception as e:
    logger.error(f"Error sending calendar image: {e}")
    return "Failed to send calendar image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize. You should still call 'academic_search_tool()' to retrieve the date information and answer the user's question."


@tool
async def send_channels_submit_complaints_image(config: RunnableConfig) -> str:
  """Send complaint submission channels image. Call this when user asks about how to submit complaints or feedback."""
  logger.info("send_channels_submit_complaints_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/channels_submit_complaints/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent complaint submission channels image to the user. [NEXT_ACTION] Respond to the user 'ดูรูปภาพเพิ่มเติมได้เลยน้าา'."

  except Exception as e:
    logger.error(f"Error sending channels submit complaints image: {e}")
    return "Failed to send complaint channels image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize."


@tool
async def send_graduated_image(config: RunnableConfig) -> str:
  """Send graduation information image. Call this when user asks about graduation."""
  logger.info("send_graduated_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/graduated/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent graduation information image to the user. [NEXT_ACTION] Respond to the user 'ดูรูปภาพเพิ่มเติมได้เลยน้าา'. Do not call 'academic_search_tool()'."

  except Exception as e:
    logger.error(f"Error sending graduated image: {e}")
    return "Failed to send graduation image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize."


@tool
async def send_registration_officer_image(config: RunnableConfig) -> str:
  """Send registration officer contact image. Call this when user asks about registration officers."""
  logger.info("send_registration_officer_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/registration_officer/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent registration officer contact image to the user. [NEXT_ACTION] Respond to the user 'ดูรูปภาพเพิ่มเติมได้เลยน้าา'."

  except Exception as e:
    logger.error(f"Error sending registration officer image: {e}")
    return "Failed to send registration officer image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize."


@tool
async def send_step_image(config: RunnableConfig) -> str:
  """Send STEP program information image. Call this when user asks about the STEP program, Intensive Courses, STEP exam."""
  logger.info("send_step_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/STEP/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent STEP program information image to the user. [NEXT_ACTION] Respond to the user 'ดูรูปภาพเพิ่มเติมได้เลยน้าา'. Do not call 'academic_search_tool()'."

  except Exception as e:
    logger.error(f"Error sending step image: {e}")
    return "Failed to send STEP image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize."


@tool
async def send_computer_department_room_image(config: RunnableConfig) -> str:
  """Send computer department room information image. Call this when user asks about the computer department room, commady room, compact room."""
  logger.info("send_computer_department_room_image tool called")
  metadata = config.get("metadata", {})
  user_id = metadata.get("user_id", "")
  platform = metadata.get("platform", "")
  
  try:
    image_urls = connector.get_images("images/computer_department_room/")

    await send_images(platform, user_id, image_urls, config)

    return "Successfully sent computer department room image to the user. [NEXT_ACTION] Respond to the user 'ดูรูปภาพเพิ่มเติมได้เลยน้าา'."

  except Exception as e:
    logger.error(f"Error sending computer department room image: {e}")
    return "Failed to send computer department room image. [NEXT_ACTION] Inform the user that the image could not be sent and apologize."