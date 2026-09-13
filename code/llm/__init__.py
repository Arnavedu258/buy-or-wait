"""
============================================================
BUY OR WAIT • LLM PACKAGE
============================================================

Enterprise AI Orchestration Layer

Purpose
-------
This package provides deterministic financial explanation
services. It NEVER modifies business calculations.

Architecture
------------
FinanceAgent
      │
      ▼
ExplanationEngine
      │
      ▼
PromptBuilder (RAG)
      │
      ▼
RetrievedContext

Design Principles
-----------------
✓ Clean Architecture
✓ SOLID
✓ Immutable DTOs
✓ Dependency Injection
✓ Thread-safe
✓ Deterministic AI
============================================================
"""

from .explanation import (
    ExplanationEngine,
    ExplanationResult,
)

from .finance_agent import (
    FinanceAgent,
    AgentResult,
)

__version__ = "1.0.0"
__author__ = "Buy Or Wait AI Team"

__all__ = [
    # Orchestrator
    "FinanceAgent",

    # Results
    "AgentResult",
    "ExplanationResult",

    # Engine
    "ExplanationEngine",
]