
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest

from engine.affordability_engine import AffordabilityEngine
from engine.planner_engine import PlannerEngine


# ==========================================================
# Affordability Engine Tests
# ==========================================================

class TestAffordabilityEngine:

    def test_safe_amount(self, state):
        engine = AffordabilityEngine()

        safe = engine.calculate_safe_amount(state)

        assert safe == Decimal("30000.00")

    def test_zero_balance(self, low_balance_state):
        engine = AffordabilityEngine()

        safe = engine.calculate_safe_amount(low_balance_state)

        assert safe == Decimal("0.00")

    @pytest.mark.parametrize(
        "balance,reserve,expected",
        [
            (50000, 10000, "40000.00"),
            (25000, 10000, "15000.00"),
            (10000, 10000, "0.00"),
            (9999, 10000, "0.00"),
            (10001, 10000, "1.00"),
        ],
    )
    def test_decimal_precision(
        self,
        profile,
        balance,
        reserve,
        expected,
    ):
        profile.minimum_balance_to_keep = reserve

        from models.state import FinancialState

        state = FinancialState(
            profile=profile,
            available_balance=Decimal(str(balance)),
            recurring_expenses=[],
            events=[],
            messages=[],
            images=[],
        )

        engine = AffordabilityEngine()

        assert (
            engine.calculate_safe_amount(state)
            == Decimal(expected)
        )


# ==========================================================
# Planner Engine Tests
# ==========================================================

class TestPlannerEngine:

    def test_full_payment(self, state, request):
        planner = PlannerEngine()

        decision = planner.plan(state, request)

        assert decision.recommended_payment_method == "FULL_PAYMENT"
        assert decision.affordability_status == "APPROVED"
        assert decision.amount_safe_to_pay >= Decimal("18000")

    def test_partial_payment(self, partial_state, request):
        planner = PlannerEngine()

        decision = planner.plan(partial_state, request)

        assert decision.recommended_payment_method == "PARTIAL_PAYMENT"
        assert decision.amount_safe_to_pay == Decimal("12000.00")

    def test_wait_strategy(self, low_balance_state, request):
        planner = PlannerEngine()

        decision = planner.plan(low_balance_state, request)

        assert decision.recommended_payment_method == "WAIT"
        assert decision.amount_safe_to_pay == Decimal("0.00")


# ==========================================================
# Deterministic Behaviour
# ==========================================================

class TestDeterminism:

    def test_same_input_same_output(self, state, request):
        planner = PlannerEngine()

        d1 = planner.plan(state, request)
        d2 = planner.plan(state, request)

        assert d1 == d2


# ==========================================================
# Thread Safety
# ==========================================================

class TestConcurrency:

    def test_parallel_execution(self, state, request):

        planner = PlannerEngine()

        def worker():
            return planner.plan(state, request)

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: worker(), range(32)))

        first = results[0]

        assert all(r == first for r in results)

    def test_no_shared_mutation(self, state, request):

        planner = PlannerEngine()

        original = state.available_balance

        planner.plan(state, request)

        assert state.available_balance == original