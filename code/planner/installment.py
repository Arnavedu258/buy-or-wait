from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Iterable, Optional

from models.payment import PaymentOption
from models.request import PaymentRequest
from models.state import FinancialState

from engine.planner_engine import (
    PaymentDecision,
    PaymentMethod,
)

from .full_payment import PaymentStrategy


# ==========================================================
# Money Utility
# ==========================================================

class Money:
    SCALE = Decimal("0.01")

    @staticmethod
    def of(value: float | Decimal) -> Decimal:
        return Decimal(str(value)).quantize(
            Money.SCALE,
            rounding=ROUND_HALF_UP,
        )


# ==========================================================
# Immutable Installment Plan
# ==========================================================

@dataclass(frozen=True, slots=True)
class InstallmentPlan:
    plan_id: str
    name: str
    months: int
    monthly_amount: Decimal
    total_amount: Decimal

    @property
    def interest_cost(self) -> Decimal:
        return self.total_amount - self.monthly_amount * self.months


# ==========================================================
# Repository Adapter
# ==========================================================

class InstallmentRepository(ABC):

    def get_by_request(
        self,
        state: FinancialState,
        request_id: str,
    ) -> list[PaymentOption]:

        return [
            option
            for option in state.payment_options
            if (
                option.request_id == request_id
                and option.plan_type.lower() == "installment"
            )
        ]


# ==========================================================
# Optimizer
# ==========================================================

class InstallmentOptimizer:
    """
    Select the financially safest plan.

    Priority
    --------
    1. Lowest monthly payment
    2. Lowest total repayment
    3. Shortest tenure
    """

    @staticmethod
    def choose(plans: Iterable[InstallmentPlan]) -> Optional[InstallmentPlan]:

        plans = list(plans)

        if not plans:
            return None

        return min(
            plans,
            key=lambda p: (
                p.monthly_amount,
                p.total_amount,
                p.months,
            ),
        )


# ==========================================================
# Installment Strategy
# ==========================================================

class InstallmentStrategy(PaymentStrategy):

    def __init__(self):
        self.repository = InstallmentRepository()
        self.optimizer = InstallmentOptimizer()

    # ------------------------------------------------------

    def _map(
        self,
        option: PaymentOption,
    ) -> InstallmentPlan:

        return InstallmentPlan(
            plan_id=str(option.option_id),
            name=option.plan_name,
            months=option.months,
            monthly_amount=Money.of(option.monthly_amount),
            total_amount=Money.of(option.total_amount),
        )

    # ------------------------------------------------------

    def _load_best_plan(
        self,
        state: FinancialState,
        request: PaymentRequest,
    ) -> InstallmentPlan:

        options = self.repository.get_by_request(
            state,
            request.request_id,
        )

        plans = [self._map(o) for o in options]

        best = self.optimizer.choose(plans)

        if best is None:
            raise ValueError(
                f"No installment plan found for {request.request_id}"
            )

        return best

    # ------------------------------------------------------

    def create(
        self,
        state: FinancialState,
        request: PaymentRequest,
        safe_amount: float,
    ) -> PaymentDecision:

        plan = self._load_best_plan(state, request)

        payment_plan = (
            f"{plan.name} | "
            f"{plan.months} monthly payments × "
            f"₹{plan.monthly_amount:,.2f}"
        )

        explanation = (
            f"Recommended {plan.name} because it provides the lowest "
            f"monthly obligation (₹{plan.monthly_amount:,.2f}) while "
            f"keeping total repayment at ₹{plan.total_amount:,.2f}. "
            "This option minimizes cash-flow pressure across the forecast horizon."
        )

        return PaymentDecision(
            amount_safe_to_pay=0.0,
            affordability_status="INSTALLMENT",
            recommended_payment_method=PaymentMethod.INSTALLMENT.value,
            payment_plan=payment_plan,
            earliest_date_for_full_payment=None,
            spending_changes_needed="",
            decision_explanation=explanation,
        )