import pytest

from payouts.models import Payout

from .factories import PayoutFactory


@pytest.mark.django_db
def test_create_payout():
    payout = PayoutFactory()
    assert payout.id is not None
    assert payout.user_id is not None
    assert payout.status == Payout.Status.PENDING
    assert payout.currency == "RUB"
    assert payout.recipient_details == {"card": "0000 1111 2222 3333"}


@pytest.mark.django_db
def test_payout_str_representation():
    payout = PayoutFactory()

    text = str(payout)

    assert str(payout.id) in text
    assert str(payout.amount) in text
    assert payout.currency in text
    assert payout.status in text
