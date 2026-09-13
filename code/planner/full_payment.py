from __future__ import annotations

from abc import ABC, abstractmethod

from models.request import PaymentRequest
from models.state import FinancialState

from engine.planner_engine import (
    PaymentDecision,
    PaymentMethod,
)


# ==========================================================
# Strategy Interface
# ==========================================================

class PaymentStrategy(ABC):

    @abstractmethod
    def create(
        self,
        state: FinancialState,
        request: PaymentRequest,
        safe_amount: float,
    ) -> PaymentDecision:
        pass


# ==========================================================
# Full Payment Strategy
# ==========================================================

class FullPaymentStrategy(PaymentStrategy):

    def create(
        self,
        state: FinancialState,
        request: PaymentRequest,
        safe_amount: float,
    ) -> PaymentDecision:

        return PaymentDecision(
            amount_safe_to_pay=round(safe_amount, 2),
            affordability_status="AFFORDABLE",
            recommended_payment_method=PaymentMethod.FULL_PAYMENT.value,
            payment_plan="Pay full amount today",
            earliest_date_for_full_payment=request.request_date.isoformat(),
            spending_changes_needed="",
            decision_explanation=(
                f"₹{safe_amount:,.2f} can be paid immediately because "
                "the projected 90-day balance never falls below the "
                "minimum balance requirement."
            ),
        )