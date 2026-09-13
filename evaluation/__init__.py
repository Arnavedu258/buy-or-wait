"""
====================================================================
BUY OR WAIT • ENTERPRISE EVALUATION LAYER
====================================================================

Purpose
-------
Offline evaluation, benchmarking, and AI quality measurement for the
Buy Or Wait Financial Decision Engine.

Architecture
------------
evaluation/
│
├── __init__.py      → Public package API
├── benchmark.py     → Performance & latency benchmark
├── scorecard.py     → ML + Financial evaluation
└── reports/         → Generated CSV / JSON reports

Design Principles
-----------------
✓ Stateless
✓ Immutable DTOs
✓ Thread-safe
✓ OS independent (pathlib)
✓ Deterministic evaluation
✓ Clean Architecture
✓ SOLID compliant

Metrics
-------
Classification
    • Accuracy
    • Precision
    • Recall
    • F1 Score

Financial
    • MAE
    • RMSE
    • Money Accuracy

RAG
    • Recall@K
    • MRR
    • Hit Rate

Performance
    • Throughput
    • P50 / P95 Latency
    • Peak Memory

Usage
-----
from evaluation import BenchmarkRunner, EvaluationEngine

benchmark = BenchmarkRunner().execute()

score = EvaluationEngine().evaluate(
    "output.csv",
    "ground_truth.csv",
)
====================================================================
"""

# ==========================================================
# Benchmark API
# ==========================================================

from .benchmark import (
    BenchmarkRunner,
    BenchmarkResult,
)

# ==========================================================
# Scorecard API
# ==========================================================

from .scorecard import (
    EvaluationEngine,
    ScoreCard,
    ScoreReport,
)

# ==========================================================
# Package Metadata
# ==========================================================

__title__ = "Buy Or Wait Evaluation Framework"
__version__ = "1.0.0"
__author__ = "Buy Or Wait AI Team"
__license__ = "MIT"

# ==========================================================
# Public Exports
# ==========================================================

__all__ = [
    "BenchmarkRunner",
    "BenchmarkResult",
    "EvaluationEngine",
    "ScoreCard",
    "ScoreReport",
]