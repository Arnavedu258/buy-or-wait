from __future__ import annotations

import sys
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import perf_counter

import polars as pl

from llm import FinanceAgent
from retrieval.validator import DatasetValidator
from utils.logger import get_logger

from evaluation import (
    BenchmarkRunner,
    EvaluationEngine,
)
from evaluation.report_generator import ReportGenerator


# ==========================================================
# CONFIGURATION
# ==========================================================

ROOT = Path(__file__).resolve().parent

DATASET_DIR = ROOT / "dataset"
GROUND_TRUTH = DATASET_DIR / "ground_truth.csv"

OUTPUT_FILE = ROOT / "output.csv"

MAX_WORKERS = 8

REQUIRED_OUTPUT_COLUMNS = [
    "request_id",
    "amount_safe_to_pay",
    "affordability_status",
    "recommended_payment_method",
    "payment_plan",
    "earliest_date_for_full_payment",
    "spending_changes_needed",
    "decision_explanation",
]


# ==========================================================
# APPLICATION
# ==========================================================

class BuyOrWaitApplication:
    """
    Enterprise AI Financial Decision Engine

    Pipeline
    --------
    Dataset Validation
            ↓
       Retrieval Layer
            ↓
       OCR / NLP / RAG
            ↓
      Financial Planner
            ↓
      LLM Explanation
            ↓
        Output CSV
            ↓
    Benchmark + Scorecard
            ↓
     Executive Reports
    """

    def __init__(self):

        self.trace_id = uuid.uuid4().hex[:12]

        self.logger = get_logger("BUY_OR_WAIT")

        self.validator = DatasetValidator(DATASET_DIR)

        self.agent = FinanceAgent()

        self.report_generator = ReportGenerator()

    # ------------------------------------------------------
    # Startup
    # ------------------------------------------------------

    def startup(self):

        self.logger.info("=" * 65)
        self.logger.info("BUY OR WAIT • AI FINANCIAL DECISION ENGINE")
        self.logger.info("=" * 65)
        self.logger.info(f"Trace ID : {self.trace_id}")

        if not DATASET_DIR.exists():
            raise FileNotFoundError(
                f"Dataset folder not found : {DATASET_DIR}"
            )

        self.validator.validate()

        self.logger.info("Dataset validation completed.")

    # ------------------------------------------------------
    # Process All Requests
    # ------------------------------------------------------

    def process_requests(self):

        self.logger.info("Building RAG Vector Index...")

        self.agent.build_vector_index()

        requests = self.agent.requests.get_all()

        if len(requests) == 0:
            raise RuntimeError("No payment requests found.")

        workers = min(
            MAX_WORKERS,
            max(2, len(requests)),
        )

        self.logger.info(
            f"Processing {len(requests)} requests using {workers} threads."
        )

        results = []

        with ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="PlannerPool",
        ) as pool:

            futures = [
                pool.submit(
                    self.agent.process_request,
                    request,
                )
                for request in requests.iter_rows(named=True)
            ]

            for future in as_completed(futures):
                results.append(future.result())

        results.sort(key=lambda x: x.request_id)

        return results

    # ------------------------------------------------------
    # Export CSV
    # ------------------------------------------------------

    def export_output(self, results):

        rows = [r.row for r in results]

        df = (
            pl.DataFrame(rows)
            .select(REQUIRED_OUTPUT_COLUMNS)
        )

        df.write_csv(OUTPUT_FILE)

        self.logger.info(f"Output exported → {OUTPUT_FILE.name}")

    # ------------------------------------------------------
    # Evaluation
    # ------------------------------------------------------

    def evaluate(self):

        benchmark = BenchmarkRunner().execute()

        score = EvaluationEngine().evaluate(
            OUTPUT_FILE,
            GROUND_TRUTH,
        )

        self.report_generator.generate(
            benchmark=benchmark,
            score=score,
        )

        return benchmark, score

    # ------------------------------------------------------
    # KPI Dashboard
    # ------------------------------------------------------

    def print_summary(
        self,
        results,
        benchmark,
        score,
        seconds,
    ):

        avg_confidence = (
            sum(r.confidence for r in results)
            / len(results)
        )

        avg_latency = (
            sum(r.latency_ms for r in results)
            / len(results)
        )

        self.logger.info("-" * 65)
        self.logger.info("EXECUTION SUMMARY")
        self.logger.info("-" * 65)

        self.logger.info(f"Requests          : {len(results)}")
        self.logger.info(f"Execution Time    : {seconds:.3f} sec")
        self.logger.info(f"Throughput        : {benchmark.throughput_rps} req/sec")
        self.logger.info(f"P95 Latency       : {benchmark.p95_latency_ms} ms")
        self.logger.info(f"Peak Memory       : {benchmark.peak_memory_mb} MB")
        self.logger.info(f"Average Latency   : {avg_latency:.2f} ms")
        self.logger.info(f"Average Confidence: {avg_confidence:.2f}")
        self.logger.info(f"Enterprise Score  : {score.final_score}/100")

        self.logger.info("-" * 65)
        self.logger.info("Generated Reports")
        self.logger.info("evaluation/reports/")
        self.logger.info("   benchmark_report.csv")
        self.logger.info("   scorecard.csv")
        self.logger.info("   scorecard.json")
        self.logger.info("   executive_report.txt")
        self.logger.info("-" * 65)

    # ------------------------------------------------------
    # Shutdown
    # ------------------------------------------------------

    def shutdown(self):

        self.logger.info("Releasing resources...")

        if hasattr(self.agent, "close"):
            self.agent.close()

        self.logger.info("Shutdown complete.")

    # ------------------------------------------------------
    # Run
    # ------------------------------------------------------

    def run(self):

        start = perf_counter()

        self.startup()

        results = self.process_requests()

        self.export_output(results)

        benchmark, score = self.evaluate()

        elapsed = perf_counter() - start

        self.print_summary(
            results,
            benchmark,
            score,
            elapsed,
        )


# ==========================================================
# ENTRY POINT
# ==========================================================

def main():

    app = BuyOrWaitApplication()

    try:

        app.run()

    except Exception as exc:

        print("\n" + "=" * 60)
        print("FATAL ERROR")
        print("=" * 60)
        print(exc)
        print("=" * 60)

        sys.exit(1)

    finally:

        app.shutdown()


if __name__ == "__main__":
    main()