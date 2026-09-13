from __future__ import annotations

from enum import Enum
from typing import Final


# ==========================================================
# ENVIRONMENT
# ==========================================================

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"


# ==========================================================
# CURRENCY
# ==========================================================

class Currency(str, Enum):
    INR = "INR"
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"


# ==========================================================
# PAYMENT STRATEGY
# ==========================================================

class PaymentMethod(str, Enum):
    FULL_PAYMENT = "FULL_PAYMENT"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    INSTALLMENT = "INSTALLMENT"
    WAIT = "WAIT"


# ==========================================================
# AFFORDABILITY
# ==========================================================

class AffordabilityStatus(str, Enum):
    AFFORDABLE = "AFFORDABLE"
    PARTIALLY_AFFORDABLE = "PARTIALLY_AFFORDABLE"
    NOT_AFFORDABLE = "NOT_AFFORDABLE"


# ==========================================================
# RISK ENGINE
# ==========================================================

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


# ==========================================================
# AI CONFIDENCE
# ==========================================================

class ConfidenceLevel(float, Enum):
    LOW = 0.40
    MEDIUM = 0.70
    HIGH = 0.90


# ==========================================================
# DATASET FILES
# ==========================================================

CSV_FILES: Final = {
    "profiles": "profiles.csv",
    "events": "events.csv",
    "requests": "requests.csv",
    "payments": "payments.csv",
    "messages": "messages.csv",
    "exchange": "exchange_rates.csv",
    "images": "image_refs.csv",
}


# ==========================================================
# IMAGE SUPPORT
# ==========================================================

SUPPORTED_IMAGE_EXTENSIONS: Final = {
    ".png",
    ".jpg",
    ".jpeg",
}


# ==========================================================
# AI / RAG CONSTANTS
# ==========================================================

EMBEDDING_DIMENSION: Final = 384

DEFAULT_TOP_K: Final = 5

MAX_CONTEXT_DOCUMENTS: Final = 12


# ==========================================================
# FINANCIAL THRESHOLDS
# ==========================================================

MIN_EMERGENCY_MONTHS: Final = 3

MAX_INSTALLMENT_MONTHS: Final = 24

SAFE_SPENDING_RATIO: Final = 0.35


# ==========================================================
# CACHE
# ==========================================================

VECTOR_CACHE_SIZE: Final = 2048

REPOSITORY_CACHE_SIZE: Final = 5000


# ==========================================================
# API
# ==========================================================

DEFAULT_TIMEOUT_SECONDS: Final = 30

MAX_WORKER_THREADS: Final = 8