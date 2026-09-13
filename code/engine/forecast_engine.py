from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta

from models.state import FinancialState
from .cashflow_engine import CashflowEngine, CashSnapshot


# ==========================================================
# Forecast DTO
# ==========================================================

@dataclass(slots=True)
class ForecastDay:
    day: date
    balance: float
    minimum_required: float
    safe: bool


# ==========================================================
# Forecast Engine
# ==========================================================

class ForecastEngine:
    """
    90-Day Rolling Forecast

    Rules
    -----
    • Confirmed salaries apply on settlement date
    • Pending debits reduce available balance
    • Pending credits ignored
    • Refunds ignored
    • Failed transactions ignored
    """

    def __init__(self):
        self.cashflow = CashflowEngine()

    # ------------------------------------------------------

    def simulate(
        self,
        state: FinancialState,
        request_date: date,
        days: int = 90,
    ) -> list[ForecastDay]:

        snapshots = self.cashflow.build_daily_cashflow(state)

        balance = state.profile.current_balance

        minimum = state.profile.minimum_balance_to_keep

        snapshot_map = {
            s.day: s for s in snapshots
        }

        forecast: list[ForecastDay] = []

        current = request_date

        for _ in range(days + 1):

            if current in snapshot_map:

                daily = snapshot_map[current]
                balance = daily.closing_balance

            forecast.append(
                ForecastDay(
                    day=current,
                    balance=round(balance, 2),
                    minimum_required=minimum,
                    safe=balance >= minimum,
                )
            )

            current += timedelta(days=1)

        return forecast

    # ------------------------------------------------------

    @staticmethod
    def minimum_balance(
        forecast: list[ForecastDay],
    ) -> float:

        return min(day.balance for day in forecast)

    # ------------------------------------------------------

    @staticmethod
    def always_safe(
        forecast: list[ForecastDay],
    ) -> bool:

        return all(day.safe for day in forecast)