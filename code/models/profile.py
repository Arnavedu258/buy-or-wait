from pydantic import BaseModel, Field
from typing import Optional


class Profile(BaseModel):
    """Represents one user from financial_profiles.csv"""

    user_id: str = Field(..., description="Primary Key")

    home_currency: str

    available_balance: float
    minimum_balance_to_keep: float

    financial_priority: str
    spending_preference: str

    payment_methods_user_will_consider: str

    max_installment_months: Optional[int] = None