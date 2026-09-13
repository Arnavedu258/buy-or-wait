from __future__ import annotations

import re
from enum import Enum


class Intent(str, Enum):
    CANCEL = "cancel"
    SETTLEMENT = "settlement"
    AMENDMENT = "amendment"
    PURCHASE = "purchase"
    INFORMATION = "information"
    UNKNOWN = "unknown"


class IntentClassifier:
    """
    Hybrid Intent Classifier

    Current:
        Rule-based (deterministic)

    Future:
        GPT / Spring AI fallback
    """

    RULES = {
        Intent.CANCEL: [
            r"\bcancel\b",
            r"\bstop\b",
            r"\bterminate\b",
            r"\bvoid\b",
        ],
        Intent.SETTLEMENT: [
            r"\bpaid\b",
            r"\bsettled\b",
            r"\bcompleted\b",
            r"\bpayment received\b",
        ],
        Intent.AMENDMENT: [
            r"\bchange\b",
            r"\bupdate\b",
            r"\bmodify\b",
            r"\breschedule\b",
        ],
        Intent.PURCHASE: [
            r"\bbuy\b",
            r"\bpurchase\b",
            r"\border\b",
            r"\bpay\b",
        ],
    }

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def classify(self, text: str) -> Intent:
        text = self.normalize(text)

        for intent, patterns in self.RULES.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    return intent

        if len(text) < 3:
            return Intent.UNKNOWN

        return Intent.INFORMATION