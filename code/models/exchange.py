from datetime import date
from pydantic import BaseModel, Field


class ExchangeRate(BaseModel):
    """Represents one currency exchange rate."""

    rate_date: date = Field(..., description="Rate date")

    from_currency: str

    to_currency: str

    rate: float