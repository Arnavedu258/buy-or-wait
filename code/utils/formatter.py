from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Any

import polars as pl


# ==========================================================
# Canonical Output Schema
# ==========================================================

OUTPUT_COLUMNS = [
    "request_id",
    "amount_safe_to_pay",
    "affordability_status",
    "recommended_payment_method",
    "payment_plan",
    "earliest_date_for_full_payment",
    "spending_changes_needed",
    "decision_explanation",
]


# ==========================================================
# Enterprise Formatter
# ==========================================================

class OutputFormatter:
    """
    Deterministic HackerRank CSV serializer.

    Guarantees
    ----------
    ✓ Stable column order
    ✓ ISO-8601 dates
    ✓ Decimal precision
    ✓ Null normalization
    ✓ Thread-safe (stateless)
    """

    SCALE = Decimal("0.01")

    # ------------------------------------------------------

    @classmethod
    def money(cls, value: Any) -> float:

        if value in (None, ""):
            return 0.00

        return float(
            Decimal(str(value)).quantize(
                cls.SCALE,
                rounding=ROUND_HALF_UP,
            )
        )

    # ------------------------------------------------------

    @staticmethod
    def iso(value: Any) -> str:

        if value is None:
            return ""

        if isinstance(value, date):
            return value.isoformat()

        if isinstance(value, datetime):
            return value.date().isoformat()

        return str(value)

    # ------------------------------------------------------

    @staticmethod
    def text(value: Any) -> str:

        if value is None:
            return ""

        return str(value).strip()

    # ------------------------------------------------------

    @classmethod
    def format_row(
        cls,
        request_id: str,
        decision,
    ) -> dict:

        row = asdict(decision)

        row["request_id"] = request_id

        row["amount_safe_to_pay"] = cls.money(
            row["amount_safe_to_pay"]
        )

        row["earliest_date_for_full_payment"] = cls.iso(
            row["earliest_date_for_full_payment"]
        )

        for column in OUTPUT_COLUMNS:

            if column == "amount_safe_to_pay":
                continue

            row[column] = cls.text(
                row.get(column)
            )

        return {
            column: row[column]
            for column in OUTPUT_COLUMNS
        }

    # ------------------------------------------------------

    @classmethod
    def dataframe(
        cls,
        rows: list[dict],
    ) -> pl.DataFrame:

        df = pl.DataFrame(rows)

        return (
            df
            .select(OUTPUT_COLUMNS)
            .sort("request_id")
        )

    # ------------------------------------------------------

    @classmethod
    def write_csv(
        cls,
        rows: list[dict],
        path,
    ) -> None:

        cls.dataframe(rows).write_csv(path)