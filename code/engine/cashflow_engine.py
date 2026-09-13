from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List

from models.state import FinancialState
from models.event import FinancialEvent


# ==========================================================
# Daily Snapshot DTO
# ==========================================================

@dataclass(slots=True)
class CashSnapshot:
    day: date
    opening_balance: float
    inflow: float
    outflow: float
    closing_balance: float


# ==========================================================
# Cashflow Engine
# ==========================================================

class CashflowEngine:
    """
    Deterministic Daily Cashflow Engine

    Rules
    -----
    ✔ Confirmed salaries increase balance
    ✔ Pending debits reserve money
    ✔ Pending credits ignored
    ✔ Failed transactions ignored
    ✔ Refunds ignored
    ✔ Investment gains ignored
    """

    CREDIT_TYPES = {"salary"}

    DEBIT_TYPES = {
        "rent",
        "subscription",
        "bill",
        "loan",
        "shopping",
        "groceries",
        "travel",
    }

    def _valid_events(
        self,
        state: FinancialState,
    ) -> List[FinancialEvent]:

        events = []

        for event in state.events:

            if event.status == "failed":
                continue

            if event.event_type == "refund":
                continue

            if event.event_type == "investment_gain":
                continue

            if (
                event.status == "pending"
                and event.event_type in self.CREDIT_TYPES
            ):
                continue

            events.append(event)

        return sorted(
            events,
            key=lambda e: e.event_date,
        )

    # ------------------------------------------------------

    def build_daily_cashflow(
        self,
        state: FinancialState,
    ) -> List[CashSnapshot]:

        balance = state.profile.current_balance

        snapshots: List[CashSnapshot] = []

        events = self._valid_events(state)

        for event in events:

            opening = balance

            inflow = 0.0
            outflow = 0.0

            if event.event_type in self.CREDIT_TYPES:

                inflow = event.amount
                balance += inflow

            else:

                outflow = event.amount
                balance -= outflow

            snapshots.append(
                CashSnapshot(
                    day=event.event_date,
                    opening_balance=round(opening, 2),
                    inflow=round(inflow, 2),
                    outflow=round(outflow, 2),
                    closing_balance=round(balance, 2),
                )
            )

        return snapshots