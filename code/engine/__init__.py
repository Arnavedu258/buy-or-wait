"""
============================================================
ENGINE PACKAGE
============================================================

Core deterministic business logic for Buy or Wait.

Execution Pipeline

FinancialState
      │
      ▼
Conflict Resolver
      │
      ▼
Cashflow Engine
      │
      ▼
90-Day Forecast
      │
      ▼
Affordability Engine
      │
      ▼
Planner Engine
      │
      ▼
Decision Verifier
============================================================
"""

from .state_builder import FinancialStateBuilder
from .cashflow_engine import CashflowEngine
from .forecast_engine import ForecastEngine
from .affordability_engine import AffordabilityEngine
from .planner_engine import PlannerEngine
from .verifier import DecisionVerifier

__version__ = "1.0.0"

__all__ = [
    "FinancialStateBuilder",
    "CashflowEngine",
    "ForecastEngine",
    "AffordabilityEngine",
    "PlannerEngine",
    "DecisionVerifier",
]