from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from payouts.models import Payout

from .factories import PayoutFactory


@pytest.mark.django_db
def test_create_payout_view():
    client = APIClient()
    payload = {
        "user_id": 123,
        "amount": 150.75,
        "payout_method": "bank_card",
        "payout_details": {"card": "0000 1111 2222 3333"},
    }

    trace_id = "aabbccdd12345"
    with patch("payouts.views.process_payout.delay") as mocked_task:
        response = client.post(
            "/api/v1/payouts/", payload, format="json", headers={"X-Request-ID": trace_id}
        )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == int(payload["user_id"])
    assert float(data["amount"]) == payload["amount"]
    assert data["payout_method"] == payload["payout_method"]
    assert data["payout_details"] == payload["payout_details"]
    assert data["status"] == Payout.Status.PENDING
    assert Payout.objects.filter(id=data["id"]).exists()

    mocked_task.assert_called_once_with(data["id"], trace_id)


@pytest.mark.django_db
def test_retrieve_payout_view():
    payout = PayoutFactory(amount=200.00)

    client = APIClient()
    url = f"/api/v1/payouts/{payout.id}/"
    response = client.get(url, format="json")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == payout.id
    assert data["amount"] == payout.amount
    assert data["status"] == payout.status
