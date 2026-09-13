"""
============================================================
PLANNER PACKAGE
============================================================

Enterprise Strategy Layer

Responsible for selecting the optimal payment strategy
after affordability analysis.

Strategies
----------
• FullPaymentStrategy
• PartialPaymentStrategy
• InstallmentStrategy
• WaitStrategy

Design Pattern
--------------
Strategy Pattern + Immutable Domain Objects
============================================================
"""

from .full_payment import (
    PaymentStrategy,
    FullPaymentStrategy,
)

from .partial_payment import (
    PartialPaymentStrategy,
    ScheduledPayment,
)

from .installment import (
    InstallmentStrategy,
    InstallmentPlan,
)

from .wait_strategy import (
    WaitStrategy,
    WaitAnalysis,
)

__version__ = "1.0.0"

__all__ = [
    # Base abstraction
    "PaymentStrategy",

    # Concrete strategies
    "FullPaymentStrategy",
    "PartialPaymentStrategy",
    "InstallmentStrategy",
    "WaitStrategy",

    # Domain DTOs
    "ScheduledPayment",
    "InstallmentPlan",
    "WaitAnalysis",
]