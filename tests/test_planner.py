from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal

import pytest

from planner.full_payment import FullPaymentStrategy
from planner.partial_payment import PartialPaymentStrategy
from planner.installment import InstallmentStrategy
from planner.wait_strategy import WaitStrategy


# ==========================================================
# Full Payment Strategy
# ==========================================================

class TestFullPaymentStrategy:

    def test_full_payment_success(self, state, request):

        strategy = FullPaymentStrategy()

        decision = strategy.create(
            state=state,
            request=request,
            safe_amount=Decimal("30000.00"),
        )

        assert decision.recommended_payment_method == "FULL_PAYMENT"
        assert decision.affordability_status == "APPROVED"
        assert decision.amount_safe_to_pay == Decimal("18000.00")

    def test_exact_amount(self, state, request):

        strategy = FullPaymentStrategy()

        request.requested_amount = Decimal("30000.00")

        decision = strategy.create(
            state=state,
            request=request,
            safe_amount=Decimal("30000.00"),
        )

        assert decision.amount_safe_to_pay == Decimal("30000.00")


# ==========================================================
# Partial Payment Strategy
# ==========================================================

class TestPartialPaymentStrategy:

    def test_partial_payment(self, partial_state, request):

        strategy = PartialPaymentStrategy()

        decision = strategy.create(
            state=partial_state,
            request=request,
            safe_amount=Decimal("12000.00"),
        )

        assert decision.recommended_payment_method == "PARTIAL_PAYMENT"
        assert decision.amount_safe_to_pay == Decimal("12000.00")

    def test_never_exceeds_safe_amount(self, partial_state, request):

        strategy = PartialPaymentStrategy()

        decision = strategy.create(
            state=partial_state,
            request=request,
            safe_amount=Decimal("10000.00"),
        )

        assert decision.amount_safe_to_pay <= Decimal("10000.00")


# ==========================================================
# Installment Strategy
# ==========================================================

class TestInstallmentStrategy:

    @pytest.mark.parametrize(
        "amount,months",
        [
            (12000, 3),
            (24000, 6),
            (36000, 12),
        ],
    )
    def test_installment_generation(self, state, request, amount, months):

        strategy = InstallmentStrategy()

        request.requested_amount = Decimal(str(amount))

        decision = strategy.create(
            state=state,
            request=request,
            months=months,
        )

        assert decision.recommended_payment_method == "INSTALLMENT"
        assert decision.payment_plan is not None

    def test_monthly_payment_positive(self, state, request):

        strategy = InstallmentStrategy()

        decision = strategy.create(
            state=state,
            request=request,
            months=6,
        )

        assert decision.amount_safe_to_pay > Decimal("0")


# ==========================================================
# Wait Strategy
# ==========================================================

class TestWaitStrategy:

    def test_wait_recommendation(self, low_balance_state, request):

        strategy = WaitStrategy()

        decision = strategy.create(
            state=low_balance_state,
            request=request,
            safe_amount=Decimal("0"),
        )

        assert decision.recommended_payment_method == "WAIT"
        assert decision.amount_safe_to_pay == Decimal("0")

    def test_wait_contains_explanation(self, low_balance_state, request):

        strategy = WaitStrategy()

        decision = strategy.create(
            state=low_balance_state,
            request=request,
            safe_amount=Decimal("0"),
        )

        assert len(decision.decision_explanation) > 20


# ==========================================================
# Strategy Pattern Integrity
# ==========================================================

class TestStrategyIntegrity:

    def test_deterministic_output(self, state, request):

        strategy = FullPaymentStrategy()

        d1 = strategy.create(
            state=state,
            request=request,
            safe_amount=Decimal("30000.00"),
        )

        d2 = strategy.create(
            state=state,
            request=request,
            safe_amount=Decimal("30000.00"),
        )

        assert d1 == d2

    def test_parallel_execution(self, state, request):

        strategy = FullPaymentStrategy()

        def worker():
            return strategy.create(
                state=state,
                request=request,
                safe_amount=Decimal("30000.00"),
            )

        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: worker(), range(32)))

        first = results[0]

        assert all(r == first for r in results)