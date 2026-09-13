from __future__ import annotations

from dataclasses import asdict
from datetime import date

from models.request import PaymentRequest
from .planner_engine import PaymentDecision, PaymentMethod


class DecisionVerifier:
    """
    Validates HackerRank output before CSV generation.

    Rules
    -----
    ✓ One row per request
    ✓ Safe amount <= requested amount
    ✓ Partial payment must contain completion date
    ✓ Completion date <= desired completion date
    ✓ Installment must contain plan name
    """

    REQUIRED_COLUMNS = [
        "request_id",
        "amount_safe_to_pay",
        "affordability_status",
        "recommended_payment_method",
        "payment_plan",
        "earliest_date_for_full_payment",
        "spending_changes_needed",
        "decision_explanation",
    ]

    # ------------------------------------------------------

    def validate(
        self,
        request: PaymentRequest,
        decision: PaymentDecision,
    ) -> None:

        if decision.amount_safe_to_pay < 0:
            raise ValueError("Negative payment is invalid.")

        if decision.amount_safe_to_pay > request.requested_amount:
            raise ValueError(
                "Safe payment exceeds requested amount."
            )

        # Partial payment rule

        if (
            decision.recommended_payment_method
            == PaymentMethod.PARTIAL_PAYMENT.value
        ):

            if decision.earliest_date_for_full_payment is None:
                raise ValueError(
                    "Partial payment requires completion date."
                )

            completion = date.fromisoformat(
                decision.earliest_date_for_full_payment
            )

            if completion > request.desired_completion_date:
                raise ValueError(
                    "Completion date exceeds desired date."
                )

        # Installment rule

        if (
            decision.recommended_payment_method
            == PaymentMethod.INSTALLMENT.value
        ):

            if not decision.payment_plan:
                raise ValueError(
                    "Installment plan is missing."
                )

    # ------------------------------------------------------

    def to_output_row(
        self,
        request: PaymentRequest,
        decision: PaymentDecision,
    ) -> dict:

        self.validate(request, decision)

        row = {
            "request_id": request.request_id,
            **asdict(decision),
        }

        return row