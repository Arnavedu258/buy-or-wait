from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from time import perf_counter

from engine.state_builder import StateBuilder
from engine.planner_engine import PlannerEngine
from engine.verifier import DecisionVerifier

from rag.vector_store import VectorStore
from rag.retriever import SemanticRetriever
from llm.explanation import ExplanationEngine

from retrieval import (
    ProfileRepository,
    RequestRepository,
    EventRepository,
    MessageRepository,
    ImageRepository,
    PaymentRepository,
    ExchangeRepository,
)


# ==========================================================
# Immutable Result
# ==========================================================

@dataclass(frozen=True, slots=True)
class AgentResult:
    request_id: str
    row: dict
    latency_ms: float
    confidence: float


# ==========================================================
# Enterprise AI Finance Agent
# ==========================================================

class FinanceAgent:

    def __init__(self):

        # repositories
        self.profiles = ProfileRepository()
        self.requests = RequestRepository()
        self.events = EventRepository()
        self.messages = MessageRepository()
        self.images = ImageRepository()
        self.payments = PaymentRepository()
        self.exchange = ExchangeRepository()

        # engines
        self.builder = StateBuilder()
        self.planner = PlannerEngine()
        self.verifier = DecisionVerifier()

        # rag
        self.vector_store = VectorStore()
        self.retriever = SemanticRetriever(self.vector_store)
        self.explainer = ExplanationEngine()

        # thread pool
        self.pool = ThreadPoolExecutor(max_workers=4)

    # ------------------------------------------------------
    # Index Messages
    # ------------------------------------------------------

    def build_vector_index(self):

        docs = []

        for row in self.messages.get_all().iter_rows(named=True):

            docs.append((
                str(row["message_id"]),
                row["content"],
                {
                    "user_id": row["user_id"],
                    "timestamp": row["timestamp"],
                    "source": "messages",
                }
            ))

        self.vector_store.add_many(docs)

    # ------------------------------------------------------
    # Single Request
    # ------------------------------------------------------

    def process_request(self, request):

        start = perf_counter()

        state = self.builder.build(
            request=request,
            profiles=self.profiles,
            events=self.events,
            messages=self.messages,
            images=self.images,
            payments=self.payments,
            exchange=self.exchange,
        )

        decision = self.planner.plan(state, request)

        contexts = self.retriever.retrieve(
            query=request.description,
            top_k=3,
            metadata_filter={"user_id": request.user_id},
        )

        explanation = self.explainer.generate(
            decision,
            contexts,
        )

        decision.decision_explanation = explanation.explanation

        row = self.verifier.to_output_row(
            request,
            decision,
        )

        latency = (perf_counter() - start) * 1000

        return AgentResult(
            request_id=request.request_id,
            row=row,
            latency_ms=round(latency, 2),
            confidence=explanation.confidence,
        )

    # ------------------------------------------------------
    # Parallel Processing
    # ------------------------------------------------------

    def run(self):

        self.build_vector_index()

        requests = self.requests.get_all()

        futures = [
            self.pool.submit(
                self.process_request,
                request,
            )
            for request in requests.iter_rows(named=True)
        ]

        results = [
            future.result()
            for future in futures
        ]

        return results