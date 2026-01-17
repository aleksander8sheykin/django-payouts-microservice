from datetime import timedelta
from decimal import Decimal

import pytest
from celery.exceptions import MaxRetriesExceededError
from django.utils import timezone

from core.tracing import get_trace_id
from payouts.models import Payout
from payouts.services import TemporaryPaymentError
from payouts.tasks import PROCESSING_DELAY, process_payout, reconcile_processing_payouts

from .factories import PayoutFactory


class DummyGatewaySuccess:
    def send_payment(self, user_id, amount, currency, recipient_details):
        return True


class DummyGatewayTemporaryError:
    def send_payment(self, user_id, amount, currency, recipient_details):
        raise TemporaryPaymentError("temporary")


@pytest.mark.django_db
def test_process_payout_success(monkeypatch):
    payout = PayoutFactory()

    monkeypatch.setattr("payouts.tasks.gateway", DummyGatewaySuccess())

    process_payout(payout.id)

    payout.refresh_from_db()
    assert payout.status == Payout.Status.PROCESSED
    assert payout.processed_at is not None


@pytest.mark.django_db
def test_process_payout_already_processing(monkeypatch, caplog):
    payout = PayoutFactory(status=Payout.Status.PROCESSING)

    monkeypatch.setattr("payouts.tasks.gateway", DummyGatewaySuccess())

    with caplog.at_level("WARNING"):
        process_payout(payout.id)
        assert f"Payout {payout.id} has invalid status" in caplog.text


@pytest.mark.django_db
def test_retrieve_payout(monkeypatch):
    payout = PayoutFactory(amount=Decimal("12.34"))

    monkeypatch.setattr("payouts.tasks.gateway", DummyGatewaySuccess())

    process_payout(payout.id)

    retrieved = Payout.objects.get(id=payout.id)
    assert retrieved.id == payout.id
    assert retrieved.user_id == payout.user_id
    assert retrieved.amount == payout.amount
    assert retrieved.currency == "RUB"
    assert retrieved.recipient_details == {"card": "0000 1111 2222 3333"}
    assert retrieved.status == Payout.Status.PROCESSED
    assert retrieved.processed_at is not None


@pytest.mark.django_db
def test_process_payout_temporary_error_marks_failed_on_max_retries(monkeypatch):
    payout = PayoutFactory()

    monkeypatch.setattr("payouts.tasks.gateway", DummyGatewayTemporaryError())

    def _raise_max_retries(*args, **kwargs):
        raise MaxRetriesExceededError()

    monkeypatch.setattr("payouts.tasks.process_payout.retry", _raise_max_retries)

    process_payout(payout.id)

    payout.refresh_from_db()
    assert payout.status == Payout.Status.FAILED


@pytest.mark.django_db
def test_reconcile_processing_payouts_marks_stuck_as_failed():
    payout = PayoutFactory(status=Payout.Status.PROCESSING)

    timeout = timezone.now() - timedelta(seconds=PROCESSING_DELAY + 1)
    Payout.objects.filter(id=payout.id).update(updated_at=timeout)

    reconcile_processing_payouts()

    payout.refresh_from_db()
    assert payout.status == Payout.Status.FAILED


@pytest.mark.django_db
def test_process_payout_uses_provided_trace_id(monkeypatch):
    payout = PayoutFactory()

    monkeypatch.setattr("payouts.tasks.gateway", DummyGatewaySuccess())

    process_payout(payout.id, trace_id="custom-trace-id")

    assert get_trace_id() == "custom-trace-id"

