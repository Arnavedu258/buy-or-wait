"""
==============================================================
BUY OR WAIT • RETRIEVAL LAYER
==============================================================

Repository Pattern + Dataset Access Layer

Responsibilities
----------------
• CSV Loading
• Repository Access
• Thread-safe Cache
• Structured Logging
==============================================================
"""

from .loader import DatasetLoader
from .cache import RepositoryCache
from .logger import RetrievalLogger

from .repositories import (
    ProfileRepository,
    RequestRepository,
    EventRepository,
    PaymentRepository,
    MessageRepository,
    ImageRepository,
    ExchangeRepository,
)

__title__ = "Buy Or Wait Retrieval Layer"
__version__ = "1.0.0"

__all__ = [
    "DatasetLoader",
    "RepositoryCache",
    "RetrievalLogger",
    "ProfileRepository",
    "RequestRepository",
    "EventRepository",
    "PaymentRepository",
    "MessageRepository",
    "ImageRepository",
    "ExchangeRepository",
]