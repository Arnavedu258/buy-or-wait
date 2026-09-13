from datetime import date
from pydantic import BaseModel, Field


class Request(BaseModel):
    """Represents one purchase request."""

    request_id: str = Field(..., description="Primary Key")

    user_id: str = Field(..., description="Foreign Key → user_profile")

    request_date: date

    request_type: str

    requested_amount: float

    desired_completion_date: date

    allows_partial_payment: bool

    request_text: str
    