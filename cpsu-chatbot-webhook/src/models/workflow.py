from pydantic import BaseModel
from typing import Literal


class WorkflowInput(BaseModel):
  input_as_text: str
  user_id: str
  conversation_id: str
  platform: Literal["facebook", "line"]


class EscalationData(BaseModel):
    latest_user_message: str
    agent: str