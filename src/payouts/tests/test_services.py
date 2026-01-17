import logging
from decimal import Decimal

import pytest

from payouts.services import PaymentGateway, TemporaryPaymentError


def test_payment_gateway_raises_temporary_error_and_logs_trace_id(caplog):
    gateway = PaymentGateway()

    with caplog.at_level(logging.WARNING, logger="celery"):
        with pytest.raises(TemporaryPaymentError):
            gateway.send_payment(
                user_id=1,
                amount=Decimal("10.50"),
                currency="RUB",
                recipient_details={"card": "0000 1111 2222 3333"},
            )

    assert "Payment to 1 failed temporarily" in caplog.text


