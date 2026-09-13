from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from engine.planner_engine import PaymentDecision
from rag.prompt_builder import PromptBuilder
from rag.retriever import RetrievedContext


# ==========================================================
# Explanation DTO
# ==========================================================

@dataclass(frozen=True, slots=True)
class ExplanationResult:
    explanation: str
    evidence_count: int
    confidence: float


# ==========================================================
# Deterministic Explanation Engine
# ==========================================================

class ExplanationEngine:
    """
    Generates deterministic financial explanations.

    This class NEVER changes the payment decision.
    It only explains why the decision was made.
    """

    def __init__(self):
        self.builder = PromptBuilder()

    # ------------------------------------------------------

    @staticmethod
    def _confidence(
        contexts: Iterable[RetrievedContext],
    ) -> float:

        scores = [c.final_score for c in contexts]

        if not scores:
            return 0.50

        return round(sum(scores) / len(scores), 2)

    # ------------------------------------------------------

    @staticmethod
    def _summarize(
        decision: PaymentDecision,
    ) -> str:

        return (
            f"Method={decision.recommended_payment_method}, "
            f"SafeAmount={decision.amount_safe_to_pay}, "
            f"Status={decision.affordability_status}"
        )

    # ------------------------------------------------------

    def generate(
        self,
        decision: PaymentDecision,
        contexts: list[RetrievedContext],
    ) -> ExplanationResult:

        summary = self._summarize(decision)

        prompt = self.builder.build(
            decision_summary=summary,
            contexts=contexts,
        )

        evidence = [
            c.text for c in contexts[:3]
        ]

        explanation = (
            f"{decision.decision_explanation} "
            f"This recommendation is supported by "
            f"{len(evidence)} financial records including: "
            + "; ".join(evidence)
            + "."
        )

        return ExplanationResult(
            explanation=explanation,
            evidence_count=len(evidence),
            confidence=self._confidence(contexts),
        )