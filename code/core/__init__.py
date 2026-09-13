"""
======================================================================
 BUY OR WAIT • CORE KERNEL
======================================================================

Enterprise shared infrastructure layer.

This package contains only immutable, reusable infrastructure:
    • Configuration
    • Constants / Enums
    • Exception hierarchy

No business logic belongs here.

Architecture
------------
core/
│
├── config.py
├── constants.py
├── exceptions.py
└── __init__.py

Used by:
    Retrieval
    RAG
    NLP
    Engine
    Planner
    API
    Evaluation

======================================================================
"""

# ==============================================================
# CONFIGURATION
# ==============================================================

from .config import (
    settings,
    get_settings,
    Settings,
)

# ==============================================================
# CONSTANTS / ENUMS
# ==============================================================

from .constants import (
    Environment,
    Currency,
    PaymentMethod,
    AffordabilityStatus,
    RiskLevel,
    ConfidenceLevel,
    CSV_FILES,
    EMBEDDING_DIMENSION,
    DEFAULT_TOP_K,
    SAFE_SPENDING_RATIO,
    MAX_INSTALLMENT_MONTHS,
)

# ==============================================================
# EXCEPTIONS
# ==============================================================

from .exceptions import (
    BuyOrWaitError,
    ErrorContext,
    DatasetValidationError,
    MissingDatasetError,
    InvalidSchemaError,
    RetrievalError,
    EmbeddingError,
    VectorStoreError,
    PlanningError,
    InsufficientFundsError,
    OCRExtractionError,
    ValidationError,
    SystemError,
)

# ==============================================================
# PACKAGE METADATA
# ==============================================================

__title__ = "Buy Or Wait Core Kernel"
__version__ = "1.0.0"
__author__ = "Buy Or Wait AI Team"
__license__ = "MIT"

# ==============================================================
# PUBLIC API
# ==============================================================

__all__ = [

    # Config
    "settings",
    "get_settings",
    "Settings",

    # Enums
    "Environment",
    "Currency",
    "PaymentMethod",
    "AffordabilityStatus",
    "RiskLevel",
    "ConfidenceLevel",

    # Constants
    "CSV_FILES",
    "EMBEDDING_DIMENSION",
    "DEFAULT_TOP_K",
    "SAFE_SPENDING_RATIO",
    "MAX_INSTALLMENT_MONTHS",

    # Exceptions
    "BuyOrWaitError",
    "ErrorContext",
    "DatasetValidationError",
    "MissingDatasetError",
    "InvalidSchemaError",
    "RetrievalError",
    "EmbeddingError",
    "VectorStoreError",
    "PlanningError",
    "InsufficientFundsError",
    "OCRExtractionError",
    "ValidationError",
    "SystemError",
]