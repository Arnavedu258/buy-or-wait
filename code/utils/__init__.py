"""
============================================================
BUY OR WAIT • UTILITIES PACKAGE
============================================================

Enterprise Infrastructure Layer

Purpose
-------
Provides shared stateless utilities used across the
entire financial decision engine.

Modules
-------
• logger      → Structured JSON logging
• formatter   → Deterministic CSV serialization
• currency    → Decimal FX conversion
• dates       → Business calendar & timelines

Design Principles
-----------------
✓ Stateless Services
✓ Thread Safe
✓ Immutable Data
✓ Deterministic Output
✓ Financial Precision
============================================================
"""

# -------------------- Logging --------------------

from .logger import (
    get_logger,
    LogContext,
)

# -------------------- CSV Formatter --------------------

from .formatter import (
    OutputFormatter,
    OUTPUT_COLUMNS,
)

# -------------------- Currency --------------------

from .currency import (
    CurrencyEngine,
    ExchangeRate,
)

# -------------------- Dates --------------------

from .dates import (
    DateService,
    DateRange,
)

# ==========================================================
# Package Metadata
# ==========================================================

__version__ = "1.0.0"
__layer__ = "Infrastructure"

# ==========================================================
# Public API
# ==========================================================

__all__ = [

    # Logging
    "get_logger",
    "LogContext",

    # Formatter
    "OutputFormatter",
    "OUTPUT_COLUMNS",

    # Currency
    "CurrencyEngine",
    "ExchangeRate",

    # Dates
    "DateService",
    "DateRange",
]