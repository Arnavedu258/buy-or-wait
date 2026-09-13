from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import polars as pl

from core import (
    CSV_FILES,
    DatasetValidationError,
    InvalidSchemaError,
    MissingDatasetError,
)


# ==========================================================
# SCHEMA CONTRACT
# ==========================================================

EXPECTED_SCHEMA = {
    "profiles.csv": [
        "user_id",
        "full_name",
        "monthly_income",
        "current_balance",
        "minimum_balance_keep",
        "preferred_currency",
    ],
    "requests.csv": [
        "request_id",
        "user_id",
        "requested_amount",
        "currency",
        "request_date",
        "description",
    ],
    "payments.csv": [
        "payment_id",
        "user_id",
        "amount",
        "currency",
        "payment_date",
    ],
    "events.csv": [
        "event_id",
        "user_id",
        "title",
        "event_date",
        "expected_amount",
        "event_type",
    ],
    "messages.csv": [
        "message_id",
        "user_id",
        "message_text",
        "message_time",
    ],
    "exchange_rates.csv": [
        "from_currency",
        "to_currency",
        "rate",
        "effective_date",
    ],
    "image_refs.csv": [
        "image_id",
        "user_id",
        "image_path",
        "ocr_amount",
    ],
}


# ==========================================================
# VALIDATION RESULT
# ==========================================================

@dataclass(frozen=True, slots=True)
class ValidationResult:
    file_name: str
    rows: int
    columns: int
    valid: bool


# ==========================================================
# DATASET VALIDATOR
# ==========================================================

class DatasetValidator:
    """
    Enterprise Dataset Validation Layer

    Thread Safe
    Stateless
    Fail Fast
    """

    def __init__(self, dataset_dir: Path):
        self.dataset_dir = Path(dataset_dir)

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def validate(self) -> list[ValidationResult]:

        results: list[ValidationResult] = []

        for csv_name in CSV_FILES.values():

            file_path = self.dataset_dir / csv_name

            df = self._load(file_path)

            self._validate_schema(csv_name, df)
            self._validate_nulls(csv_name, df)
            self._validate_duplicates(csv_name, df)

            results.append(
                ValidationResult(
                    file_name=csv_name,
                    rows=df.height,
                    columns=df.width,
                    valid=True,
                )
            )

        return results

    # ------------------------------------------------------
    # Load CSV
    # ------------------------------------------------------

    @staticmethod
    def _load(path: Path) -> pl.DataFrame:

        if not path.exists():
            raise MissingDatasetError(path)

        return pl.read_csv(path)

    # ------------------------------------------------------
    # Schema Validation
    # ------------------------------------------------------

    @staticmethod
    def _validate_schema(
        file_name: str,
        df: pl.DataFrame,
    ) -> None:

        expected = EXPECTED_SCHEMA.get(file_name)

        if expected is None:
            return

        received = list(df.columns)

        if received != expected:
            raise InvalidSchemaError(
                file=file_name,
                expected=expected,
                received=received,
            )

    # ------------------------------------------------------
    # Null Validation
    # ------------------------------------------------------

    @staticmethod
    def _validate_nulls(
        file_name: str,
        df: pl.DataFrame,
    ) -> None:

        null_count = (
            df.null_count()
            .sum_horizontal()
            .item()
        )

        if null_count > 0:
            raise DatasetValidationError(
                f"{file_name} contains {null_count} null values."
            )

    # ------------------------------------------------------
    # Duplicate Primary Key
    # ------------------------------------------------------

    @staticmethod
    def _validate_duplicates(
        file_name: str,
        df: pl.DataFrame,
    ) -> None:

        primary_keys = {
            "profiles.csv": "user_id",
            "requests.csv": "request_id",
            "payments.csv": "payment_id",
            "events.csv": "event_id",
            "messages.csv": "message_id",
            "image_refs.csv": "image_id",
        }

        key = primary_keys.get(file_name)

        if key is None:
            return

        duplicates = (
            df.group_by(key)
              .len()
              .filter(pl.col("len") > 1)
        )

        if duplicates.height > 0:
            raise DatasetValidationError(
                f"Duplicate primary key detected in {file_name} ({key})"
            )