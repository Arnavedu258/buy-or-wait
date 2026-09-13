from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest

from models.profile import UserProfile
from models.request import PaymentRequest
from models.state import FinancialState


# ==========================================================
# USER PROFILE
# Session scope = created once for entire suite
# ==========================================================

@pytest.fixture(scope="session")
def profile() -> UserProfile:

    return UserProfile(
        user_id="USR001",
        monthly_income=50000,
        minimum_balance_to_keep=10000,
        preferred_currency="INR",
    )


# ==========================================================
# PAYMENT REQUEST
# Fresh object for every test
# ==========================================================

@pytest.fixture(scope="function")
def request() -> PaymentRequest:

    return PaymentRequest(
        request_id="REQ001",
        user_id="USR001",
        requested_amount=18000,
        currency="INR",
        request_date=date(2026, 9, 13),
        description="Purchase Laptop",
    )


# ==========================================================
# FINANCIAL STATE
# Clean immutable state every test
# ==========================================================

@pytest.fixture(scope="function")
def state(profile) -> FinancialState:

    return FinancialState(
        profile=profile,
        available_balance=Decimal("40000.00"),
        recurring_expenses=[],
        events=[],
        messages=[],
        images=[],
    )


# ==========================================================
# LOW BALANCE STATE
# ==========================================================

@pytest.fixture(scope="function")
def low_balance_state(profile) -> FinancialState:

    return FinancialState(
        profile=profile,
        available_balance=Decimal("8000.00"),
        recurring_expenses=[],
        events=[],
        messages=[],
        images=[],
    )


# ==========================================================
# PARTIAL PAYMENT STATE
# ==========================================================

@pytest.fixture(scope="function")
def partial_state(profile) -> FinancialState:

    return FinancialState(
        profile=profile,
        available_balance=Decimal("22000.00"),
        recurring_expenses=[],
        events=[],
        messages=[],
        images=[],
    )