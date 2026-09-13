from __future__ import annotations

import os
import statistics
import tracemalloc
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter, process_time

import polars as pl

from llm.finance_agent import FinanceAgent
from utils.logger import get_logger

# ==========================================================
# Benchmark Result DTO
# ==========================================================

@dataclass(frozen=True, slots=True)
class BenchmarkResult:
    total_requests: int
    worker_threads: int

    total_time_sec: float
    cpu_time_sec: float

    throughput_rps: float

    p50_latency_ms: float
    p95_latency_ms: float

    peak_memory_mb: float

# ==========================================================
# Enterprise Benchmark Runner
# ==========================================================

class BenchmarkRunner:

    WARMUP_REQUESTS = 5

    def __init__(self):

        self.logger = get_logger("BENCHMARK")

        self.agent = FinanceAgent()

    # ------------------------------------------------------

    def warmup(self):

        requests = self.agent.requests.get_all()

        for row in requests.head(self.WARMUP_REQUESTS).iter_rows(named=True):

            self.agent.process_request(row)

    # ------------------------------------------------------

    def execute(self):

        self.agent.build_vector_index()

        self.warmup()

        requests = self.agent.requests.get_all()

        workers = min(
            os.cpu_count() or 4,
            8,
        )

        latencies = []

        tracemalloc.start()

        wall_start = perf_counter()
        cpu_start = process_time()

        with ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="PlannerPool",
        ) as executor:

            futures = [
                executor.submit(
                    self.agent.process_request,
                    row,
                )
                for row in requests.iter_rows(named=True)
            ]

            for future in as_completed(futures):

                result = future.result()

                latencies.append(result.latency_ms)

        cpu = process_time() - cpu_start
        wall = perf_counter() - wall_start

        _, peak = tracemalloc.get_traced_memory()

        tracemalloc.stop()

        p50 = statistics.median(latencies)

        p95 = statistics.quantiles(
            latencies,
            n=20,
        )[18]

        return BenchmarkResult(
            total_requests=len(latencies),
            worker_threads=workers,
            total_time_sec=round(wall, 3),
            cpu_time_sec=round(cpu, 3),
            throughput_rps=round(len(latencies) / wall, 2),
            p50_latency_ms=round(p50, 2),
            p95_latency_ms=round(p95, 2),
            peak_memory_mb=round(
                peak / 1024 / 1024,
                2,
            ),
        )

    # ------------------------------------------------------

    @staticmethod
    def save(report: BenchmarkResult):

        output = Path("evaluation/reports")

        output.mkdir(parents=True, exist_ok=True)

        df = pl.DataFrame([report.__dict__])

        df.write_csv(output / "benchmark_report.csv")

# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":

    runner = BenchmarkRunner()

    report = runner.execute()

    runner.save(report)

    print("\n" + "=" * 58)
    print(" BUY OR WAIT • PERFORMANCE BENCHMARK")
    print("=" * 58)

    print(f"Requests        : {report.total_requests}")
    print(f"Workers         : {report.worker_threads}")
    print(f"Wall Time       : {report.total_time_sec} sec")
    print(f"CPU Time        : {report.cpu_time_sec} sec")
    print(f"Throughput      : {report.throughput_rps} req/sec")
    print(f"P50 Latency     : {report.p50_latency_ms} ms")
    print(f"P95 Latency     : {report.p95_latency_ms} ms")
    print(f"Peak Memory     : {report.peak_memory_mb} MB")

    print("=" * 58)