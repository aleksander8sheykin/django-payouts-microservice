import logging
from decimal import Decimal

logger = logging.getLogger("celery")


class PaymentGatewayError(Exception):
    pass


class TemporaryPaymentError(PaymentGatewayError):
    pass


class PaymentGateway:
    def send_payment(
        self, user_id: int, amount: Decimal, currency: str, recipient_details: dict
    ) -> bool:
        """
        Попытка выполнить платёж.
        Возвращает True, если успешно, иначе бросает TemporaryPaymentError
        """
        trace_id = get_trace_id()
        request_headers = {"X-Request-ID": trace_id}
        logger.info(
            "Sending payment %s %s to %s",
            amount,
            currency,
            user_id,
            extra={"trace_id": trace_id},
        )

        # ------------------------------
        # TODO: здесь реальный вызов внешнего сервиса
        # response = requests.post(..., headers=request_headers), grpc_client.send(...)
        result = False
        # ------------------------------

        if result:
            logger.info(
                "Payment to %s succeeded",
                user_id,
                extra={"trace_id": get_trace_id()},
            )
            return True
        else:
            logger.warning(
                "Payment to %s failed temporarily",
                user_id,
                extra={"trace_id": get_trace_id()},
            )
            raise TemporaryPaymentError("Payment service temporarily unavailable")
from core.tracing import get_trace_id
