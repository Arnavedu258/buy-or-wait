from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Tuple

from models.request import PaymentRequest
from models.state import FinancialState

from engine.planner_engine import (
    PaymentDecision,
    PaymentMethod,
)

from .full_payment import PaymentStrategy


# ==========================================================
# Immutable Payment Installment
# ==========================================================

@dataclass(frozen=True, slots=True)
class ScheduledPayment:
    payment_date: date
    amount: Decimal


# ==========================================================
# Enterprise Partial Payment Strategy
# ==========================================================

class PartialPaymentStrategy(PaymentStrategy):
    """
    Creates an optimized two-payment schedule.

    Business Rules
    --------------
    • Exactly two payments
    • Payment 1 = Safe amount today
    • Payment 2 = Remaining amount
    • Completion <= desired completion date
    """

    MONEY = Decimal("0.01")

    # ------------------------------------------------------
    # Decimal Helper
    # ------------------------------------------------------

    @classmethod
    def _money(cls, value: float | Decimal) -> Decimal:
        return Decimal(str(value)).quantize(
            cls.MONEY,
            rounding=ROUND_HALF_UP,
        )

    # ------------------------------------------------------
    # Schedule Builder
    # ------------------------------------------------------

    def build_schedule(
        self,
        request: PaymentRequest,
        safe_amount: float,
    ) -> Tuple[ScheduledPayment, ScheduledPayment]:

        today_amount = self._money(safe_amount)

        remaining = (
            self._money(request.requested_amount)
            - today_amount
        )

        completion = min(
            request.desired_completion_date,
            request.request_date.replace(
                day=request.request_date.day
            ),
        )

        second = ScheduledPayment(
            payment_date=completion,
            amount=remaining,
        )

        first = ScheduledPayment(
            payment_date=request.request_date,
            amount=today_amount,
        )

        self._validate(first, second, request)

        return first, second

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    @classmethod
    def _validate(
        cls,
        first: ScheduledPayment,
        second: ScheduledPayment,
        request: PaymentRequest,
    ) -> None:

        if first.amount <= 0:
            raise ValueError("First payment must be positive.")

        if second.amount <= 0:
            raise ValueError("Remaining payment must be positive.")

        total = first.amount + second.amount

        expected = cls._money(request.requested_amount)

        if total != expected:
            raise ValueError(
                "Two payments must equal requested amount."
            )

        if second.payment_date > request.desired_completion_date:
            raise ValueError(
                "Completion exceeds desired completion date."
            )

    # ------------------------------------------------------
    # Strategy Entry
    # ------------------------------------------------------

    def create(
        self,
        state: FinancialState,
        request: PaymentRequest,
        safe_amount: float,
    ) -> PaymentDecision:

        first, second = self.build_schedule(
            request,
            safe_amount,
        )

        plan = (
            f"1) ₹{first.amount} on {first.payment_date.isoformat()} | "
            f"2) ₹{second.amount} on {second.payment_date.isoformat()}"
        )

        return PaymentDecision(
            amount_safe_to_pay=float(first.amount),
            affordability_status="PARTIAL",
            recommended_payment_method=PaymentMethod.PARTIAL_PAYMENT.value,
            payment_plan=plan,
            earliest_date_for_full_payment=second.payment_date.isoformat(),
            spending_changes_needed=(
                "Reduce optional recurring subscriptions until "
                "the second payment is completed."
            ),
            decision_explanation=(
                f"Pay ₹{first.amount} safely today. "
                f"The remaining ₹{second.amount} can be paid on "
                f"{second.payment_date.isoformat()} while preserving "
                "the minimum required balance throughout the 90-day forecast."
            ),
        )