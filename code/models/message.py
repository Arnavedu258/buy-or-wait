from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Message(BaseModel):
    """Represents one message from messages.csv"""

    message_id: str = Field(..., description="Primary Key")

    user_id: str

    request_id: Optional[str] = None

    related_event_id: Optional[str] = None

    message_date: date

    source: str

    content: str