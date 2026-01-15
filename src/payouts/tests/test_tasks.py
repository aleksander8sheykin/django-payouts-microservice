from decimal import Decimal

import pytest

from payouts.models import Payout
from payouts.tasks import process_payout

from .factories import PayoutFactory


@pytest.mark.django_db
def test_process_payout_success(monkeypatch):
    payout = PayoutFactory()

    class DummyGateway:
        def send_payment(self, user_id, amount, payout_method, payout_details):
            return True

    monkeypatch.setattr("payouts.tasks.gateway", DummyGateway())

    process_payout(payout.id)

    payout.refresh_from_db()
    assert payout.status == Payout.Status.PROCESSED
    assert payout.processed_at is not None


@pytest.mark.django_db
def test_process_payout_already_processing(monkeypatch, caplog):
    payout = PayoutFactory(status=Payout.Status.PROCESSING)

    class DummyGateway:
        def send_payment(self, user_id, amount, payout_method, payout_details):
            return True

    monkeypatch.setattr("payouts.tasks.gateway", DummyGateway())

    with caplog.at_level("WARNING"):
        process_payout(payout.id)
        assert f"Payout {payout.id} has invalid status" in caplog.text


@pytest.mark.django_db
def test_retrieve_payout(monkeypatch):
    payout = PayoutFactory(amount=Decimal("12.34"))

    class DummyGateway:
        def send_payment(self, user_id, amount, payout_method, payout_details):
            return True

    monkeypatch.setattr("payouts.tasks.gateway", DummyGateway())

    process_payout(payout.id)

    retrieved = Payout.objects.get(id=payout.id)
    assert retrieved.id == payout.id
    assert retrieved.user_id == payout.user_id
    assert retrieved.amount == payout.amount
    assert retrieved.payout_method == Payout.PayoutMethod.BANK_CARD
    assert retrieved.payout_details == {"card": "0000 1111 2222 3333"}
    assert retrieved.status == Payout.Status.PROCESSED
    assert retrieved.processed_at is not None
