from typing import Optional
from pydantic import BaseModel, Field


class ImageReference(BaseModel):
    """Represents one image from images.csv"""

    image_id: str = Field(..., description="Primary Key")

    user_id: str

    request_id: Optional[str] = None

    related_event_id: Optional[str] = None

    image_path: str