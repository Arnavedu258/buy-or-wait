from __future__ import annotations

from dataclasses import dataclass, field
from threading import RLock
from typing import Any, Iterable, Optional

import numpy as np

from .embedding import Embedding, EmbeddingEngine


# ==========================================================
# Immutable Vector Record
# ==========================================================

@dataclass(frozen=True, slots=True)
class VectorRecord:
    id: str
    text: str
    vector: np.ndarray
    metadata: dict[str, Any] = field(default_factory=dict)


# ==========================================================
# Search Result DTO
# ==========================================================

@dataclass(frozen=True, slots=True)
class SearchResult:
    id: str
    text: str
    score: float
    metadata: dict[str, Any]


# ==========================================================
# Enterprise Vector Store
# ==========================================================

class VectorStore:
    """
    Thread-safe semantic vector index.

    Design Goals
    ------------
    • Immutable records
    • Lock-protected writes
    • Zero-copy reads
    • Deterministic ranking
    """

    def __init__(self):
        self._engine = EmbeddingEngine()
        self._records: list[VectorRecord] = []
        self._matrix = np.empty(
            (0, EmbeddingEngine.DIMENSION),
            dtype=np.float32,
        )
        self._lock = RLock()

    # ------------------------------------------------------
    # Index single document
    # ------------------------------------------------------

    def add(
        self,
        record_id: str,
        text: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> None:

        embedding: Embedding = self._engine.embed(text)

        if metadata is None:
            metadata = {}

        record = VectorRecord(
            id=record_id,
            text=text,
            vector=embedding.vector,
            metadata=metadata,
        )

        with self._lock:
            self._records.append(record)

            self._matrix = np.vstack(
                [self._matrix, embedding.vector]
            )

    # ------------------------------------------------------
    # Bulk indexing
    # ------------------------------------------------------

    def add_many(
        self,
        documents: Iterable[tuple[str, str, dict]],
    ) -> None:

        for doc_id, text, meta in documents:
            self.add(doc_id, text, meta)

    # ------------------------------------------------------
    # Search
    # ------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 5,
        threshold: float = 0.15,
        metadata_filter: Optional[dict[str, Any]] = None,
    ) -> list[SearchResult]:

        if len(self._records) == 0:
            return []

        query_vector = self._engine.embed(query).vector

        scores = self._matrix @ query_vector

        ranked = np.argsort(scores)[::-1]

        results: list[SearchResult] = []

        for index in ranked:

            score = float(scores[index])

            if score < threshold:
                continue

            record = self._records[index]

            if metadata_filter:
                matched = all(
                    record.metadata.get(k) == v
                    for k, v in metadata_filter.items()
                )

                if not matched:
                    continue

            results.append(
                SearchResult(
                    id=record.id,
                    text=record.text,
                    score=round(score, 4),
                    metadata=record.metadata,
                )
            )

            if len(results) >= top_k:
                break

        return results

    # ------------------------------------------------------
    # Statistics
    # ------------------------------------------------------

    @property
    def size(self) -> int:
        return len(self._records)

    @property
    def dimension(self) -> int:
        return EmbeddingEngine.DIMENSION

    def clear(self) -> None:
        with self._lock:
            self._records.clear()
            self._matrix = np.empty(
                (0, self.dimension),
                dtype=np.float32,
            )