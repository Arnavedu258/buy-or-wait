from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from enum import Enum

from models.request import PaymentRequest
from models.state import FinancialState

from .affordability_engine import (
    AffordabilityEngine,
    AffordabilityStatus,
)


# ==========================================================
# Payment Method Enum
# ==========================================================

class PaymentMethod(str, Enum):
    FULL_PAYMENT = "FULL_PAYMENT"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    INSTALLMENT = "INSTALLMENT"
    WAIT = "WAIT"


# ==========================================================
# Final Decision DTO
# ==========================================================

@dataclass(slots=True)
class PaymentDecision:
    amount_safe_to_pay: float
    affordability_status: str
    recommended_payment_method: str
    payment_plan: str
    earliest_date_for_full_payment: str | None
    spending_changes_needed: str
    decision_explanation: str


# ==========================================================
# Planner Engine
# ==========================================================

class PlannerEngine:

    def __init__(self):
        self.affordability = AffordabilityEngine()

    # ------------------------------------------------------

    def _installment_available(
        self,
        state: FinancialState,
        request: PaymentRequest,
    ) -> str | None:

        for option in state.payment_options:

            if option.request_id != request.request_id:
                continue

            if option.plan_type.lower() == "installment":
                return option.plan_name

        return None

    # ------------------------------------------------------

    def plan(
        self,
        state: FinancialState,
        request: PaymentRequest,
    ) -> PaymentDecision:

        result = self.affordability.evaluate(state, request)

        # ---------- FULL PAYMENT ----------

        if result.status == AffordabilityStatus.AFFORDABLE:

            return PaymentDecision(
                amount_safe_to_pay=result.safe_amount,
                affordability_status=result.status.value,
                recommended_payment_method=PaymentMethod.FULL_PAYMENT.value,
                payment_plan="Pay full amount today",
                earliest_date_for_full_payment=request.request_date.isoformat(),
                spending_changes_needed="",
                decision_explanation=(
                    "Current cashflow safely supports the full payment "
                    "while maintaining the required minimum balance."
                ),
            )

        # ---------- PARTIAL PAYMENT ----------

        if result.status == AffordabilityStatus.PARTIAL:

            remaining = (
                request.requested_amount - result.safe_amount
            )

            completion = min(
                request.request_date + timedelta(days=30),
                request.desired_completion_date,
            )

            return PaymentDecision(
                amount_safe_to_pay=result.safe_amount,
                affordability_status=result.status.value,
                recommended_payment_method=PaymentMethod.PARTIAL_PAYMENT.value,
                payment_plan=(
                    f"Pay {result.safe_amount:.2f} today and "
                    f"{remaining:.2f} on {completion.isoformat()}"
                ),
                earliest_date_for_full_payment=completion.isoformat(),
                spending_changes_needed="Reduce flexible subscriptions if needed",
                decision_explanation=(
                    "A partial payment is financially safe today. "
                    "The remaining balance should be paid before the desired completion date."
                ),
            )

        # ---------- INSTALLMENT ----------

        emi = self._installment_available(state, request)

        if emi:

            return PaymentDecision(
                amount_safe_to_pay=0.0,
                affordability_status="INSTALLMENT",
                recommended_payment_method=PaymentMethod.INSTALLMENT.value,
                payment_plan=emi,
                earliest_date_for_full_payment=None,
                spending_changes_needed="",
                decision_explanation=(
                    "A supported installment plan is available and is safer than paying in full."
                ),
            )

        # ---------- WAIT ----------

        return PaymentDecision(
            amount_safe_to_pay=0.0,
            affordability_status=result.status.value,
            recommended_payment_method=PaymentMethod.WAIT.value,
            payment_plan="Wait until sufficient confirmed income arrives",
            earliest_date_for_full_payment=None,
            spending_changes_needed="Reduce optional recurring expenses",
            decision_explanation=(
                "Paying now would violate the minimum balance requirement."
            ),
        )