from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Iterable

import numpy as np


# ==========================================================
# Immutable Embedding DTO
# ==========================================================

@dataclass(frozen=True, slots=True)
class Embedding:
    text: str
    vector: np.ndarray


# ==========================================================
# Enterprise Embedding Engine
# ==========================================================

class EmbeddingEngine:
    """
    Offline deterministic embedding engine.

    Features
    --------
    • Internet-free
    • Cyber-safe
    • Reproducible vectors
    • 384 dimensions
    • L2 normalized
    """

    DIMENSION = 384

    TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9₹$€.]+")

    # ------------------------------------------------------

    @staticmethod
    def normalize(text: str) -> str:
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ------------------------------------------------------

    def tokenize(self, text: str) -> list[str]:
        text = self.normalize(text)
        return self.TOKEN_PATTERN.findall(text)

    # ------------------------------------------------------

    @classmethod
    def _hash(cls, token: str) -> int:
        digest = hashlib.sha256(token.encode("utf-8")).digest()
        return int.from_bytes(digest[:8], "big") % cls.DIMENSION

    # ------------------------------------------------------

    def embed(self, text: str) -> Embedding:

        vector = np.zeros(
            self.DIMENSION,
            dtype=np.float32,
        )

        tokens = self.tokenize(text)

        for token in tokens:
            index = self._hash(token)
            vector[index] += 1.0

        norm = np.linalg.norm(vector)

        if norm > 0:
            vector /= norm

        return Embedding(
            text=text,
            vector=vector,
        )

    # ------------------------------------------------------

    def embed_many(
        self,
        texts: Iterable[str],
    ) -> list[Embedding]:

        return [self.embed(text) for text in texts]

    # ------------------------------------------------------

    @staticmethod
    def cosine_similarity(
        a: np.ndarray,
        b: np.ndarray,
    ) -> float:

        return float(np.dot(a, b))