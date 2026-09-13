from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class FinancialEvent(BaseModel):
    """Represents one financial transaction/event."""

    event_id: str = Field(..., description="Primary Key")

    user_id: str = Field(..., description="Foreign Key → user_profile")

    event_date: date

    event_type: str          # salary, expense, emi, transfer

    category: str            # groceries, rent, salary...

    amount: Optional[float] = None

    currency: str

    status: str              # confirmed, pending, failed

    recurring: bool

    flexible: bool

    linked_event_id: Optional[str] = None