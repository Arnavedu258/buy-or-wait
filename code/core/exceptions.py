from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any


# ==========================================================
# ERROR CONTEXT
# ==========================================================

@dataclass(frozen=True, slots=True)
class ErrorContext:
    """
    Immutable enterprise error payload.
    """

    code: str
    message: str
    retryable: bool
    timestamp: str
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ==========================================================
# BASE EXCEPTION
# ==========================================================

class BuyOrWaitError(Exception):
    """
    Root exception for the entire application.
    """

    ERROR_CODE = "APP-000"
    RETRYABLE = False

    def __init__(
        self,
        message: str,
        **details: Any,
    ):
        super().__init__(message)

        self.context = ErrorContext(
            code=self.ERROR_CODE,
            message=message,
            retryable=self.RETRYABLE,
            timestamp=datetime.now(UTC).isoformat(),
            details=details,
        )

    def to_dict(self):
        return self.context.to_dict()

    def __str__(self):
        return f"[{self.context.code}] {self.context.message}"


# ==========================================================
# DATASET ERRORS
# ==========================================================

class DatasetValidationError(BuyOrWaitError):
    ERROR_CODE = "DATA-001"


class MissingDatasetError(DatasetValidationError):
    ERROR_CODE = "DATA-002"

    def __init__(self, path):
        super().__init__(
            "Required dataset not found.",
            path=str(path),
        )


class InvalidSchemaError(DatasetValidationError):
    ERROR_CODE = "DATA-003"

    def __init__(self, file, expected, received):
        super().__init__(
            "CSV schema mismatch.",
            file=file,
            expected=expected,
            received=received,
        )


# ==========================================================
# RAG ERRORS
# ==========================================================

class RetrievalError(BuyOrWaitError):
    ERROR_CODE = "RAG-100"
    RETRYABLE = True


class EmbeddingError(RetrievalError):
    ERROR_CODE = "RAG-101"


class VectorStoreError(RetrievalError):
    ERROR_CODE = "RAG-102"


# ==========================================================
# PLANNER ERRORS
# ==========================================================

class PlanningError(BuyOrWaitError):
    ERROR_CODE = "PLAN-200"


class InsufficientFundsError(PlanningError):
    ERROR_CODE = "PLAN-201"

    def __init__(self, balance, requested):
        super().__init__(
            "Insufficient safe balance.",
            balance=balance,
            requested=requested,
        )


# ==========================================================
# OCR ERRORS
# ==========================================================

class OCRExtractionError(BuyOrWaitError):
    ERROR_CODE = "OCR-300"
    RETRYABLE = True


# ==========================================================
# API VALIDATION
# ==========================================================

class ValidationError(BuyOrWaitError):
    ERROR_CODE = "API-400"


# ==========================================================
# SYSTEM
# ==========================================================

class SystemError(BuyOrWaitError):
    ERROR_CODE = "SYS-500"
    RETRYABLE = True