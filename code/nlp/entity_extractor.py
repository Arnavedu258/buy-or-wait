from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


# ==========================================================
# Extracted Entity Model
# ==========================================================

@dataclass(slots=True)
class ExtractedEntity:
    amount: Optional[float] = None
    currency: Optional[str] = None
    merchant: Optional[str] = None
    event_id: Optional[str] = None
    date: Optional[str] = None


# ==========================================================
# Entity Extractor
# ==========================================================

class EntityExtractor:
    """
    Extracts structured financial entities from messages.

    Supports:
        • Amount
        • Currency
        • Merchant
        • Event ID
        • ISO Date
    """

    AMOUNT_REGEX = [
        r"₹\s?([\d,]+(?:\.\d+)?)",
        r"rs\.?\s?([\d,]+(?:\.\d+)?)",
        r"inr\s?([\d,]+(?:\.\d+)?)",
        r"\$([\d,]+(?:\.\d+)?)",
        r"€([\d,]+(?:\.\d+)?)",
    ]

    DATE_REGEX = (
        r"\b\d{4}-\d{2}-\d{2}\b"
    )

    EVENT_REGEX = (
        r"\bEVT[-_]?\d+\b"
    )

    MERCHANT_REGEX = (
        r"(?:to|at|from)\s+([A-Z][A-Za-z0-9 &]+)"
    )

    CURRENCIES = {
        "₹": "INR",
        "rs": "INR",
        "inr": "INR",
        "$": "USD",
        "€": "EUR",
    }

    # ------------------------------------------------------

    @staticmethod
    def normalize(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip())

    # ------------------------------------------------------

    def extract_amount(self, text: str):

        for pattern in self.AMOUNT_REGEX:

            match = re.search(pattern, text, re.IGNORECASE)

            if match:
                value = float(match.group(1).replace(",", ""))

                symbol = text[match.start()]

                currency = self.CURRENCIES.get(
                    symbol.lower(),
                    "INR"
                )

                return value, currency

        return None, None

    # ------------------------------------------------------

    def extract_date(self, text: str):

        match = re.search(self.DATE_REGEX, text)

        if not match:
            return None

        try:
            return datetime.strptime(
                match.group(),
                "%Y-%m-%d"
            ).date().isoformat()
        except ValueError:
            return None

    # ------------------------------------------------------

    def extract_event(self, text: str):

        match = re.search(
            self.EVENT_REGEX,
            text,
            re.IGNORECASE
        )

        return match.group().upper() if match else None

    # ------------------------------------------------------

    def extract_merchant(self, text: str):

        match = re.search(self.MERCHANT_REGEX, text)

        if match:
            return match.group(1).strip()

        return None

    # ------------------------------------------------------

    def extract(self, text: str) -> ExtractedEntity:

        text = self.normalize(text)

        amount, currency = self.extract_amount(text)

        return ExtractedEntity(
            amount=amount,
            currency=currency,
            merchant=self.extract_merchant(text),
            event_id=self.extract_event(text),
            date=self.extract_date(text),
        )