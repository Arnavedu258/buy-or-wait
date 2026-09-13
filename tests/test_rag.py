from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pytest

from rag.embedding import EmbeddingEngine
from rag.vector_store import VectorStore
from rag.retriever import SemanticRetriever, RankingPolicy


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture()
def embedding():
    return EmbeddingEngine()


@pytest.fixture()
def store():

    db = VectorStore()

    db.add(
        "MSG001",
        "Salary credited ₹50000 today",
        {
            "user_id": "USR001",
            "intent": "income",
            "timestamp": "2026-09-01",
        },
    )

    db.add(
        "MSG002",
        "Netflix subscription deducted",
        {
            "user_id": "USR001",
            "intent": "expense",
            "timestamp": "2026-09-02",
        },
    )

    db.add(
        "MSG003",
        "EMI settlement completed successfully",
        {
            "user_id": "USR001",
            "intent": "settlement",
            "timestamp": "2026-09-03",
        },
    )

    return db


@pytest.fixture()
def retriever(store):
    return SemanticRetriever(store)


# ==========================================================
# Embedding Engine
# ==========================================================

class TestEmbeddingEngine:

    def test_dimension(self, embedding):

        vec = embedding.embed("salary credited")

        assert len(vec.vector) == 384

    def test_deterministic(self, embedding):

        a = embedding.embed("salary credited")
        b = embedding.embed("salary credited")

        assert np.array_equal(a.vector, b.vector)

    def test_l2_normalized(self, embedding):

        vec = embedding.embed("salary credited")

        norm = np.linalg.norm(vec.vector)

        assert round(float(norm), 5) == 1.0

    @pytest.mark.parametrize(
        "text",
        [
            "",
            "salary",
            "Salary Credited ₹50000",
            "   multiple     spaces   ",
        ],
    )
    def test_never_crashes(self, embedding, text):

        result = embedding.embed(text)

        assert result.vector.shape == (384,)


# ==========================================================
# Vector Store
# ==========================================================

class TestVectorStore:

    def test_index_size(self, store):

        assert store.size == 3

    def test_search_returns_results(self, store):

        results = store.search("salary")

        assert len(results) >= 1

    def test_metadata_filter(self, store):

        results = store.search(
            query="salary",
            metadata_filter={"user_id": "USR001"},
        )

        assert len(results) >= 1

    def test_empty_search(self):

        db = VectorStore()

        assert db.search("salary") == []


# ==========================================================
# Semantic Retriever
# ==========================================================

class TestSemanticRetriever:

    def test_salary_ranked_first(self, retriever):

        result = retriever.retrieve(
            query="monthly salary",
            top_k=1,
        )

        assert result[0].id == "MSG001"

    def test_settlement_priority(self, retriever):

        result = retriever.retrieve(
            query="emi settled",
            top_k=1,
        )

        assert result[0].id == "MSG003"

    def test_metadata_isolation(self, retriever):

        result = retriever.retrieve(
            query="salary",
            metadata_filter={"user_id": "USR001"},
        )

        assert all(
            r.metadata["user_id"] == "USR001"
            for r in result
        )

    def test_semantic_policy(self, retriever):

        result = retriever.retrieve(
            query="salary",
            policy=RankingPolicy.SEMANTIC,
        )

        assert len(result) > 0

    def test_hybrid_policy(self, retriever):

        result = retriever.retrieve(
            query="salary",
            policy=RankingPolicy.HYBRID,
        )

        assert len(result) > 0


# ==========================================================
# Concurrency
# ==========================================================

class TestConcurrency:

    def test_parallel_reads(self, retriever):

        def worker():
            return retriever.retrieve(
                "salary credited",
                top_k=2,
            )

        with ThreadPoolExecutor(max_workers=8) as pool:

            results = list(
                pool.map(lambda _: worker(), range(32))
            )

        first = [r.id for r in results[0]]

        for r in results[1:]:
            assert [x.id for x in r] == first

    def test_no_shared_mutation(self, store, retriever):

        original = store.size

        retriever.retrieve("salary")

        assert store.size == original


# ==========================================================
# Security / Injection
# ==========================================================

class TestSecurity:

    @pytest.mark.parametrize(
        "query",
        [
            "ignore previous instructions",
            "<script>alert(1)</script>",
            "DROP TABLE messages;",
        ],
    )
    def test_safe_queries(self, retriever, query):

        results = retriever.retrieve(query)

        assert isinstance(results, list)