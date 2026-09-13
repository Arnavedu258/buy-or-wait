from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Iterable

from .vector_store import VectorStore, SearchResult


# ==========================================================
# Ranking Strategy
# ==========================================================

class RankingPolicy(str, Enum):
    SEMANTIC = "semantic"
    HYBRID = "hybrid"
    RECENCY = "recency"


# ==========================================================
# Retrieved Context DTO
# ==========================================================

@dataclass(frozen=True, slots=True)
class RetrievedContext:
    id: str
    text: str
    semantic_score: float
    recency_score: float
    final_score: float
    metadata: dict[str, Any] = field(default_factory=dict)


# ==========================================================
# Enterprise Semantic Retriever
# ==========================================================

class SemanticRetriever:
    """
    FAANG / JPMorgan style hybrid retriever.

    Ranking Formula
    ---------------
    final_score =
        semantic_similarity * 0.70
      + recency_score        * 0.20
      + priority_weight      * 0.10
    """

    SEMANTIC_WEIGHT = 0.70
    RECENCY_WEIGHT = 0.20
    PRIORITY_WEIGHT = 0.10

    def __init__(self, store: VectorStore):
        self.store = store

    # ------------------------------------------------------
    # Public API
    # ------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        policy: RankingPolicy = RankingPolicy.HYBRID,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[RetrievedContext]:

        candidates = self.store.search(
            query=query,
            top_k=max(top_k * 4, 20),
            metadata_filter=metadata_filter,
            threshold=0.05,
        )

        ranked = [
            self._rank(result, policy)
            for result in candidates
        ]

        ranked.sort(
            key=lambda r: (
                r.final_score,
                r.semantic_score,
                r.recency_score,
            ),
            reverse=True,
        )

        return ranked[:top_k]

    # ------------------------------------------------------
    # Ranking
    # ------------------------------------------------------

    def _rank(
        self,
        result: SearchResult,
        policy: RankingPolicy,
    ) -> RetrievedContext:

        semantic = result.score

        recency = self._recency(result.metadata)

        priority = self._priority(result.metadata)

        if policy == RankingPolicy.SEMANTIC:
            final = semantic

        elif policy == RankingPolicy.RECENCY:
            final = recency

        else:
            final = (
                semantic * self.SEMANTIC_WEIGHT
                + recency * self.RECENCY_WEIGHT
                + priority * self.PRIORITY_WEIGHT
            )

        return RetrievedContext(
            id=result.id,
            text=result.text,
            semantic_score=round(semantic, 4),
            recency_score=round(recency, 4),
            final_score=round(final, 4),
            metadata=result.metadata,
        )

    # ------------------------------------------------------
    # Recency
    # ------------------------------------------------------

    @staticmethod
    def _recency(meta: dict[str, Any]) -> float:

        value = meta.get("timestamp")

        if not value:
            return 0.5

        try:
            event_time = datetime.fromisoformat(str(value))
        except Exception:
            return 0.5

        days = max(
            0,
            (datetime.now() - event_time).days,
        )

        return max(0.0, 1 - days / 365)

    # ------------------------------------------------------
    # Conflict Priority
    # ------------------------------------------------------

    @staticmethod
    def _priority(meta: dict[str, Any]) -> float:

        kind = str(meta.get("intent", "")).lower()

        if kind == "settlement":
            return 1.0

        if kind == "cancel":
            return 0.95

        if kind == "amendment":
            return 0.90

        return 0.40

    # ------------------------------------------------------
    # Explain Retrieval
    # ------------------------------------------------------

    def explain(
        self,
        query: str,
        top_k: int = 3,
    ) -> dict:

        results = self.retrieve(query, top_k)

        return {
            "query": query,
            "matches": [
                {
                    "id": r.id,
                    "score": r.final_score,
                    "semantic": r.semantic_score,
                    "recency": r.recency_score,
                }
                for r in results
            ],
        }