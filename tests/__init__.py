"""
====================================================================
BUY OR WAIT • ENTERPRISE TEST SUITE
====================================================================

Purpose
-------
Centralized testing package for the AI Financial Decision Engine.

Architecture
------------
tests/
│
├── conftest.py          → Shared immutable fixtures
├── test_engine.py       → Business rule validation
├── test_planner.py      → Strategy Pattern tests
├── test_rag.py          → RAG & semantic retrieval tests
└── test_utils.py        → Infrastructure & utility tests

Testing Principles
------------------
✓ Deterministic
✓ Thread-safe
✓ Platform independent
✓ Financial precision (Decimal)
✓ No shared mutable state
✓ High coverage business validation

Execution
---------
pytest tests -v
pytest tests --cov=code --cov-report=term-missing
====================================================================
"""

__title__ = "Buy Or Wait Test Suite"
__version__ = "1.0.0"
__author__ = "Buy Or Wait AI Team"

__all__ = [
    "__title__",
    "__version__",
    "__author__",
]