from datetime import date
from pydantic import BaseModel, Field


class PaymentOption(BaseModel):
    """Represents one installment/payment option."""

    payment_option_id: str = Field(..., description="Primary Key")

    request_id: str = Field(..., description="Foreign Key → request")

    payment_method: str

    number_of_payments: int

    interval_days: int

    first_payment_date: date

    financing_fee: float

    total_payable: float