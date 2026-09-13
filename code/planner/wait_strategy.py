from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from models.request import PaymentRequest
from models.state import FinancialState

from engine.forecast_engine import ForecastEngine
from engine.planner_engine import (
    PaymentDecision,
    PaymentMethod,
)

from .full_payment import PaymentStrategy


# ==========================================================
# Wait Analysis DTO
# ==========================================================

@dataclass(frozen=True, slots=True)
class WaitAnalysis:
    earliest_safe_date: Optional[date]
    peak_balance: Decimal
    minimum_balance: Decimal
    deficit: Decimal


# ==========================================================
# Wait Strategy
# ==========================================================

class WaitStrategy(PaymentStrategy):
    """
    Conservative payment recommendation.

    Rules
    -----
    • Never recommend payment if minimum balance is violated.
    • Search the 90-day forecast for the earliest safe day.
    • Recommend reducing only optional recurring expenses.
    """

    SCALE = Decimal("0.01")

    def __init__(self):
        self.forecast_engine = ForecastEngine()

    # ------------------------------------------------------
    # Money helper
    # ------------------------------------------------------

    @classmethod
    def money(cls, value: float) -> Decimal:
        return Decimal(str(value)).quantize(
            cls.SCALE,
            rounding=ROUND_HALF_UP,
        )

    # ------------------------------------------------------
    # Forecast analysis
    # ------------------------------------------------------

    def analyze(
        self,
        state: FinancialState,
        request: PaymentRequest,
    ) -> WaitAnalysis:

        forecast = self.forecast_engine.simulate(
            state=state,
            request_date=request.request_date,
        )

        reserve = self.money(
            state.profile.minimum_balance_to_keep
        )

        requested = self.money(request.requested_amount)

        earliest = None

        balances = []

        for day in forecast:

            balance = self.money(day.balance)

            balances.append(balance)

            if earliest is None and balance - requested >= reserve:
                earliest = day.day

        peak = max(balances)
        minimum = min(balances)

        deficit = max(
            Decimal("0.00"),
            reserve + requested - peak,
        )

        return WaitAnalysis(
            earliest_safe_date=earliest,
            peak_balance=peak,
            minimum_balance=minimum,
            deficit=deficit,
        )

    # ------------------------------------------------------
    # Strategy entry
    # ------------------------------------------------------

    def create(
        self,
        state: FinancialState,
        request: PaymentRequest,
        safe_amount: float,
    ) -> PaymentDecision:

        report = self.analyze(state, request)

        if report.earliest_safe_date:
            plan = (
                f"Wait until {report.earliest_safe_date.isoformat()} "
                "before paying."
            )

            explanation = (
                f"Current balance cannot safely support ₹{request.requested_amount:,.2f}. "
                f"The earliest projected safe date is "
                f"{report.earliest_safe_date.isoformat()}."
            )

            earliest = report.earliest_safe_date.isoformat()

        else:
            plan = (
                "Do not purchase within the current 90-day forecast window."
            )

            explanation = (
                f"Even the highest projected balance "
                f"(₹{report.peak_balance:,.2f}) is insufficient to safely "
                f"cover the requested payment while preserving the minimum reserve."
            )

            earliest = None

        return PaymentDecision(
            amount_safe_to_pay=0.0,
            affordability_status="WAIT",
            recommended_payment_method=PaymentMethod.WAIT.value,
            payment_plan=plan,
            earliest_date_for_full_payment=earliest,
            spending_changes_needed=(
                "Reduce optional subscriptions, entertainment, "
                "and other flexible recurring expenses only."
            ),
            decision_explanation=explanation,
        )