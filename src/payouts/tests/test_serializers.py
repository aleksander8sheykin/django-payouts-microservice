from decimal import Decimal

import pytest

from payouts.models import Payout
from payouts.serializers import (
    PayoutSerializer,
    PayoutStatusUpdateSerializer,
)


def test_payout_serializer_rejects_non_positive_amount():
    serializer = PayoutSerializer(
        data={
            "user_id": 1,
            "amount": Decimal("0.00"),
            "currency": "RUB",
            "recipient_details": {"card": "0000 1111 2222 3333"},
        }
    )

    assert not serializer.is_valid()
    assert "amount" in serializer.errors


def test_payout_status_update_serializer_valid_status():
    serializer = PayoutStatusUpdateSerializer(
        data={"status": Payout.Status.PROCESSED}
    )

    assert serializer.is_valid(), serializer.errors
    assert serializer.validated_data["status"] == Payout.Status.PROCESSED


def test_payout_status_update_serializer_invalid_status():
    serializer = PayoutStatusUpdateSerializer(data={"status": "invalid"})

    assert not serializer.is_valid()
    assert "status" in serializer.errors


