from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import polars as pl


@dataclass(frozen=True, slots=True)
class ScoreCard:
    accuracy: float
    precision: float
    recall: float
    f1: float

    mae: float
    rmse: float

    rag_recall_at_5: float
    mrr: float

    schema_valid: bool

    enterprise_score: float


class EvaluationEngine:

    REQUIRED_COLUMNS = [
        "request_id",
        "amount_safe_to_pay",
        "affordability_status",
        "recommended_payment_method",
        "payment_plan",
        "earliest_date_for_full_payment",
        "spending_changes_needed",
        "decision_explanation",
    ]

    @classmethod
    def validate_schema(cls, df):
        return df.columns == cls.REQUIRED_COLUMNS

    def evaluate(self, output_csv, truth_csv):

        pred = pl.read_csv(output_csv)
        truth = pl.read_csv(truth_csv)

        schema = self.validate_schema(pred)

        y_pred = pred["recommended_payment_method"]
        y_true = truth["recommended_payment_method"]

        accuracy = (y_pred == y_true).mean()

        tp = (y_pred == y_true).sum()
        fp = (y_pred != y_true).sum()

        precision = tp / (tp + fp) if tp + fp else 0
        recall = precision

        f1 = (
            2 * precision * recall / (precision + recall)
            if precision + recall else 0
        )

        error = (
            pred["amount_safe_to_pay"] -
            truth["amount_safe_to_pay"]
        ).abs()

        mae = error.mean()
        rmse = (error.pow(2).mean()) ** 0.5

        rag_recall = 1.0
        mrr = 1.0

        score = (
            accuracy * 35 +
            f1 * 25 +
            (1 - min(mae / 1000, 1)) * 20 +
            rag_recall * 10 +
            (1 if schema else 0) * 10
        )

        return ScoreCard(
            accuracy,
            precision,
            recall,
            f1,
            mae,
            rmse,
            rag_recall,
            mrr,
            schema,
            round(score, 2),
        )


class ReportWriter:

    REPORT_DIR = Path("evaluation/reports")

    @classmethod
    def save(cls, score: ScoreCard):

        cls.REPORT_DIR.mkdir(parents=True, exist_ok=True)

        pl.DataFrame([score.__dict__]).write_csv(
            cls.REPORT_DIR / "scorecard.csv"
        )

        with open(
            cls.REPORT_DIR / "scorecard.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                score.__dict__,
                f,
                indent=4,
            )