from typing import Optional

from pydantic import BaseModel, Field


class Decision(BaseModel):
    """Final output for one request."""

    request_id: str = Field(..., description="Request ID")

    amount_safe_to_pay: float

    affordability_status: str

    recommended_payment_method: str

    payment_plan: str

    earliest_date_for_full_payment: Optional[str] = None

    spending_changes_needed: str

    decision_explanation: str