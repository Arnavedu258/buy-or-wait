from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from models.state import FinancialState
from models.request import PaymentRequest

from .forecast_engine import ForecastEngine


# ==========================================================
# Status Enum
# ==========================================================

class AffordabilityStatus(str, Enum):
    AFFORDABLE = "AFFORDABLE"
    PARTIAL = "PARTIAL"
    WAIT = "WAIT"


# ==========================================================
# Decision DTO
# ==========================================================

@dataclass(slots=True)
class AffordabilityResult:
    safe_amount: float
    status: AffordabilityStatus
    minimum_balance_after_payment: float


# ==========================================================
# Affordability Engine
# ==========================================================

class AffordabilityEngine:

    def __init__(self):
        self.forecast = ForecastEngine()

    # ------------------------------------------------------

    def evaluate(
        self,
        state: FinancialState,
        request: PaymentRequest,
    ) -> AffordabilityResult:

        forecast = self.forecast.simulate(
            state=state,
            request_date=request.request_date,
        )

        minimum_balance = min(day.balance for day in forecast)

        reserve = state.profile.minimum_balance_to_keep

        available = max(0.0, minimum_balance - reserve)

        safe_amount = min(
            available,
            request.requested_amount,
        )

        if safe_amount >= request.requested_amount:
            status = AffordabilityStatus.AFFORDABLE

        elif safe_amount > 0:
            status = AffordabilityStatus.PARTIAL

        else:
            status = AffordabilityStatus.WAIT

        return AffordabilityResult(
            safe_amount=round(safe_amount, 2),
            status=status,
            minimum_balance_after_payment=round(
                minimum_balance,
                2,
            ),
        )