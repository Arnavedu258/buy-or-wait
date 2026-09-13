from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from functools import lru_cache
from typing import Iterable


# ==========================================================
# Immutable Date Range
# ==========================================================

@dataclass(frozen=True, slots=True)
class DateRange:
    start: date
    end: date

    @property
    def days(self) -> int:
        return (self.end - self.start).days + 1


# ==========================================================
# Enterprise Date Service
# ==========================================================

class DateService:
    """
    Centralized financial calendar utility.

    Features
    --------
    • ISO parsing
    • Business-day calculation
    • Weekend adjustment
    • Rolling 90-day timeline
    • Cached parsing
    """

    FORECAST_WINDOW = 90

    # ------------------------------------------------------
    # Parsing
    # ------------------------------------------------------

    @staticmethod
    @lru_cache(maxsize=4096)
    def parse(value: str) -> date:
        return datetime.fromisoformat(value).date()

    @staticmethod
    def iso(value: date) -> str:
        return value.isoformat()

    # ------------------------------------------------------
    # Business Calendar
    # ------------------------------------------------------

    @staticmethod
    def is_weekend(day: date) -> bool:
        return day.weekday() >= 5

    @classmethod
    def next_business_day(cls, day: date) -> date:

        current = day

        while cls.is_weekend(current):
            current += timedelta(days=1)

        return current

    @classmethod
    def previous_business_day(cls, day: date) -> date:

        current = day

        while cls.is_weekend(current):
            current -= timedelta(days=1)

        return current

    # ------------------------------------------------------
    # Timeline
    # ------------------------------------------------------

    @classmethod
    def timeline(
        cls,
        start: date,
        days: int = FORECAST_WINDOW,
    ) -> list[date]:

        return [
            start + timedelta(days=i)
            for i in range(days + 1)
        ]

    @classmethod
    def range(
        cls,
        start: date,
        end: date,
    ) -> DateRange:

        if end < start:
            raise ValueError("End date before start.")

        return DateRange(start, end)

    # ------------------------------------------------------
    # Financial Helpers
    # ------------------------------------------------------

    @classmethod
    def within_forecast(
        cls,
        request_date: date,
        target: date,
    ) -> bool:

        limit = request_date + timedelta(days=cls.FORECAST_WINDOW)

        return request_date <= target <= limit

    @staticmethod
    def earliest(
        dates: Iterable[date],
    ) -> date | None:

        dates = list(dates)

        return min(dates) if dates else None

    @staticmethod
    def latest(
        dates: Iterable[date],
    ) -> date | None:

        dates = list(dates)

        return max(dates) if dates else None

    # ------------------------------------------------------
    # Difference
    # ------------------------------------------------------

    @staticmethod
    def days_between(
        start: date,
        end: date,
    ) -> int:

        return (end - start).days