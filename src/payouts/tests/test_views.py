import re
from decimal import Decimal
from unittest.mock import patch

import pytest
from rest_framework.test import APIClient

from payouts.models import Payout
from payouts.serializers import PayoutSerializer
from payouts.views import PayoutRetrieveUpdateDeleteView

from .factories import PayoutFactory


TRACE_ID_REGEX = re.compile(r"^[a-f0-9]{32}$")


@pytest.fixture()
def api_client():
    return APIClient()


@pytest.fixture()
def payout_payload():
    return {
        "user_id": 123,
        "amount": 150.75,
        "currency": "RUB",
        "recipient_details": {"card": "0000 1111 2222 3333"},
        "comment": "Оплата бонуса",
    }


@pytest.mark.django_db
def test_create_payout_view(api_client, payout_payload):

    trace_id = "aabbccdd12345"
    with patch("payouts.views.process_payout.apply_async") as mocked_task:
        response = api_client.post(
            "/api/payouts/",
            payout_payload,
            format="json",
            headers={"X-Request-ID": trace_id},
        )

    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == int(payout_payload["user_id"])
    assert Decimal(str(data["amount"])) == Decimal(str(payout_payload["amount"]))
    assert data["currency"] == payout_payload["currency"]
    assert data["recipient_details"] == payout_payload["recipient_details"]
    assert data["comment"] == payout_payload["comment"]
    assert data["status"] == Payout.Status.PENDING
    assert Payout.objects.filter(id=data["id"]).exists()

    mocked_task.assert_called_once()
    _, kwargs = mocked_task.call_args
    assert kwargs["args"] == (data["id"],)
    assert kwargs["headers"] == {"trace_id": trace_id}


@pytest.mark.django_db
def test_create_payout_generates_trace_id(api_client, payout_payload):

    with patch("payouts.views.process_payout.apply_async") as mocked_task:
        response = api_client.post("/api/payouts/", payout_payload, format="json")

    assert response.status_code == 201
    trace_id = response.headers.get("X-Request-ID")
    assert trace_id
    assert TRACE_ID_REGEX.match(trace_id)

    data = response.json()
    mocked_task.assert_called_once()
    _, kwargs = mocked_task.call_args
    assert kwargs["args"] == (data["id"],)
    assert kwargs["headers"] == {"trace_id": trace_id}


@pytest.mark.django_db
def test_retrieve_payout_view(api_client):
    payout = PayoutFactory(amount=Decimal("200.00"))

    url = f"/api/payouts/{payout.id}/"
    response = api_client.get(url, format="json")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == payout.id
    assert Decimal(str(data["amount"])) == payout.amount
    assert data["status"] == payout.status
    assert "recipient_details" not in data
    assert "comment" not in data


@pytest.mark.django_db
def test_list_payouts_view(api_client):
    PayoutFactory(user_id=100)
    PayoutFactory(user_id=100)
    PayoutFactory(user_id=200)

    response = api_client.get("/api/payouts/?user_id=100", format="json")

    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 2
    assert data["next"] is None
    assert data["previous"] is None
    assert "results" in data
    assert len(data["results"]) == 2
    assert "recipient_details" not in data["results"][0]
    assert "comment" not in data["results"][0]

    response_without_user_id = api_client.get("/api/payouts/", format="json")

    assert response_without_user_id.status_code == 200
    empty_data = response_without_user_id.json()
    assert empty_data["count"] == 0
    assert empty_data["results"] == []


@pytest.mark.django_db
def test_patch_payout_status_view(api_client):
    payout = PayoutFactory()

    response = api_client.patch(
        f"/api/payouts/{payout.id}/",
        {"status": Payout.Status.PROCESSED},
        format="json",
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == Payout.Status.PROCESSED


@pytest.mark.django_db
def test_delete_payout_view(api_client):
    payout = PayoutFactory()

    response = api_client.delete(f"/api/payouts/{payout.id}/")

    assert response.status_code == 204
    assert not Payout.objects.filter(id=payout.id).exists()


@pytest.mark.django_db
def test_create_payout_invalid_amount(api_client, payout_payload):
    payout_payload["amount"] = 0

    response = api_client.post("/api/payouts/", payout_payload, format="json")

    assert response.status_code == 400
    data = response.json()
    assert "amount" in data


@pytest.mark.django_db
def test_patch_payout_status_invalid_value(api_client):
    payout = PayoutFactory()

    response = api_client.patch(
        f"/api/payouts/{payout.id}/",
        {"status": "invalid"},
        format="json",
    )

    assert response.status_code == 400
    data = response.json()
    assert "status" in data


def test_retrieve_update_delete_view_delete_uses_base_serializer():
    from rest_framework.test import APIRequestFactory

    factory = APIRequestFactory()
    request = factory.delete("/api/payouts/1/")

    view = PayoutRetrieveUpdateDeleteView()
    view.request = request

    assert view.get_serializer_class() is PayoutSerializer
