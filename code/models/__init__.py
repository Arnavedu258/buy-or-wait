"""
==============================================================
BUY OR WAIT • DOMAIN MODEL PACKAGE
==============================================================

Domain Driven Design (DDD)

This package contains immutable business entities only.
No repositories, no services, no business logic.

Models
------
- Profile
- PurchaseRequest
- Payment
- FinancialEvent
- Message
- ImageReference
- ExchangeRate
- Decision
- FinancialState
==============================================================
"""

# ==========================================================
# Domain Entities
# ==========================================================

from .profile import Profile
from .request import PurchaseRequest
from .payment import Payment
from .event import FinancialEvent
from .message import Message
from .image_ref import ImageReference
from .exchange import ExchangeRate
from .decision import Decision
from .state import FinancialState

# ==========================================================
# Package Metadata
# ==========================================================

__title__ = "Buy Or Wait Domain Models"
__version__ = "1.0.0"

# ==========================================================
# Public API
# ==========================================================

__all__ = [
    "Profile",
    "PurchaseRequest",
    "Payment",
    "FinancialEvent",
    "Message",
    "ImageReference",
    "ExchangeRate",
    "Decision",
    "FinancialState",
]