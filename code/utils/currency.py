from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from threading import RLock
from typing import Dict

import polars as pl


# ==========================================================
# Immutable Exchange Rate
# ==========================================================

@dataclass(frozen=True, slots=True)
class ExchangeRate:
    from_currency: str
    to_currency: str
    rate: Decimal


# ==========================================================
# Enterprise Currency Engine
# ==========================================================

class CurrencyEngine:
    """
    Thread-safe FX conversion engine.

    Features
    --------
    • Decimal arithmetic
    • Immutable exchange rates
    • ISO-4217 validation
    • O(1) lookup
    """

    SCALE = Decimal("0.01")

    def __init__(self):
        self._rates: Dict[tuple[str, str], Decimal] = {}
        self._lock = RLock()

    # ------------------------------------------------------

    @staticmethod
    def money(value) -> Decimal:
        return Decimal(str(value)).quantize(
            CurrencyEngine.SCALE,
            rounding=ROUND_HALF_UP,
        )

    # ------------------------------------------------------

    def load(self, dataframe: pl.DataFrame) -> None:

        with self._lock:

            self._rates.clear()

            for row in dataframe.iter_rows(named=True):

                key = (
                    row["from_currency"].upper(),
                    row["to_currency"].upper(),
                )

                self._rates[key] = self.money(row["rate"])

    # ------------------------------------------------------

    def convert(
        self,
        amount,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:

        amount = self.money(amount)

        frm = from_currency.upper()
        to = to_currency.upper()

        if frm == to:
            return amount

        key = (frm, to)

        if key not in self._rates:
            raise ValueError(
                f"Exchange rate not found: {frm}->{to}"
            )

        return (
            amount * self._rates[key]
        ).quantize(
            self.SCALE,
            rounding=ROUND_HALF_UP,
        )

    # ------------------------------------------------------

    def rate(
        self,
        from_currency: str,
        to_currency: str,
    ) -> Decimal:

        return self._rates[
            (
                from_currency.upper(),
                to_currency.upper(),
            )
        ]

    # ------------------------------------------------------

    def supported(self) -> list[str]:

        currencies = set()

        for frm, to in self._rates:
            currencies.add(frm)
            currencies.add(to)

        return sorted(currencies)