from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from .extractor import OCRResult


# ==========================================================
# Amount DTO
# ==========================================================

@dataclass(slots=True)
class DetectedAmount:
    amount: float
    currency: str
    confidence: float
    raw_text: str


# ==========================================================
# Amount Detector
# ==========================================================

class AmountDetector:
    """
    Extracts monetary values from OCR results.

    Supported:
        ₹45,670
        Rs 1200
        INR 9000
        $450
        €220
    """

    AMOUNT_PATTERN = re.compile(
        r"(₹|rs\.?|inr|\$|€)\s*([\d,]+(?:\.\d{1,2})?)",
        re.IGNORECASE,
    )

    CURRENCY_MAP = {
        "₹": "INR",
        "rs": "INR",
        "rs.": "INR",
        "inr": "INR",
        "$": "USD",
        "€": "EUR",
    }

    # ------------------------------------------------------

    def detect(
        self,
        results: list[OCRResult],
    ) -> Optional[DetectedAmount]:

        candidates: list[DetectedAmount] = []

        for result in results:

            match = self.AMOUNT_PATTERN.search(result.text)

            if not match:
                continue

            symbol = match.group(1).lower()

            value = float(
                match.group(2).replace(",", "")
            )

            candidates.append(
                DetectedAmount(
                    amount=value,
                    currency=self.CURRENCY_MAP[symbol],
                    confidence=result.confidence,
                    raw_text=result.text,
                )
            )

        if not candidates:
            return None

        candidates.sort(
            key=lambda x: (x.confidence, x.amount),
            reverse=True,
        )

        return candidates[0]