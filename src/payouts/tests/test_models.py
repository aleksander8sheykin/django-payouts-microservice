import pytest

from payouts.models import Payout

from .factories import PayoutFactory


@pytest.mark.django_db
def test_create_payout():
    payout = PayoutFactory()
    assert payout.id is not None
    assert payout.user_id is not None
    assert payout.status == Payout.Status.PENDING
    assert payout.payout_method == Payout.PayoutMethod.BANK_CARD
    assert payout.payout_details == {"card": "0000 1111 2222 3333"}
