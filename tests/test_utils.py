from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date
from decimal import Decimal

import polars as pl
import pytest

from utils.currency import CurrencyEngine
from utils.dates import DateService
from utils.formatter import OutputFormatter
from utils.logger import LogContext


# ==========================================================
# Currency Engine
# ==========================================================

class TestCurrencyEngine:

    @pytest.fixture()
    def engine(self):
        fx = CurrencyEngine()

        df = pl.DataFrame({
            "from_currency": ["USD", "EUR"],
            "to_currency": ["INR", "INR"],
            "rate": [83.00, 95.50],
        })

        fx.load(df)
        return fx

    def test_exact_conversion(self, engine):

        amount = engine.convert(
            100,
            "USD",
            "INR",
        )

        assert amount == Decimal("8300.00")

    def test_same_currency(self, engine):

        assert engine.convert(
            500,
            "INR",
            "INR",
        ) == Decimal("500.00")

    def test_rounding(self, engine):

        assert engine.money(12.3456) == Decimal("12.35")

    def test_supported(self, engine):

        assert "USD" in engine.supported()
        assert "EUR" in engine.supported()


# ==========================================================
# Date Service
# ==========================================================

class TestDateService:

    def test_business_day(self):

        saturday = date(2026, 9, 12)

        monday = DateService.next_business_day(saturday)

        assert monday == date(2026, 9, 14)

    def test_previous_business_day(self):

        sunday = date(2026, 9, 13)

        friday = DateService.previous_business_day(sunday)

        assert friday.weekday() == 4

    def test_timeline(self):

        days = DateService.timeline(
            date(2026, 1, 1),
            days=5,
        )

        assert len(days) == 6

    def test_forecast_window(self):

        assert DateService.within_forecast(
            date(2026, 1, 1),
            date(2026, 3, 20),
        )


# ==========================================================
# Formatter
# ==========================================================

class TestFormatter:

    def test_money_precision(self):

        assert OutputFormatter.money(
            10.126
        ) == 10.13

    def test_iso_date(self):

        assert (
            OutputFormatter.iso(
                date(2026, 5, 1)
            )
            == "2026-05-01"
        )

    def test_text_cleanup(self):

        assert (
            OutputFormatter.text(
                " hello "
            )
            == "hello"
        )


# ==========================================================
# Logger
# ==========================================================

class TestLogger:

    def test_trace_generation(self):

        trace = LogContext.new_trace()

        assert isinstance(trace, str)
        assert len(trace) == 16

    def test_request_context(self):

        LogContext.set_request("REQ001")

        assert LogContext.request() == "REQ001"


# ==========================================================
# Concurrency
# ==========================================================

class TestThreadSafety:

    def test_parallel_currency_reads(self):

        fx = CurrencyEngine()

        df = pl.DataFrame({
            "from_currency": ["USD"],
            "to_currency": ["INR"],
            "rate": [83.00],
        })

        fx.load(df)

        def worker():
            return fx.convert(
                100,
                "USD",
                "INR",
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(
                pool.map(lambda _: worker(), range(32))
            )

        assert all(
            r == Decimal("8300.00")
            for r in results
        )

    def test_parallel_dates(self):

        def worker():
            return DateService.next_business_day(
                date(2026, 9, 12)
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(
                pool.map(lambda _: worker(), range(32))
            )

        assert all(
            r == date(2026, 9, 14)
            for r in results
        )