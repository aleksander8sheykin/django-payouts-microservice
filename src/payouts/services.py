import logging
from decimal import Decimal

logger = logging.getLogger("celery")


class PaymentGatewayError(Exception):
    pass


class TemporaryPaymentError(PaymentGatewayError):
    pass


class PaymentGateway:
    def send_payment(
        self, user_id: int, amount: Decimal, payout_method: str, payout_details: dict
    ) -> bool:
        """
        Попытка выполнить платёж.
        Возвращает True, если успешно, иначе бросает TemporaryPaymentError
        """
        logger.info(f"Sending payment {amount} to {user_id} by {payout_method}")

        # ------------------------------
        # TODO: здесь реальный вызов внешнего сервиса
        # response = requests.post(...), grpc_client.send(...)
        result = False
        # ------------------------------

        if result:
            logger.info(f"Payment to {user_id} by {payout_method} succeeded")
            return True
        else:
            logger.warning(f"Payment to {user_id} by {payout_method} failed temporarily")
            raise TemporaryPaymentError("Payment service temporarily unavailable")
