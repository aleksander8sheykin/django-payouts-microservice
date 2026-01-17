import logging
import os
from datetime import timedelta

from celery import shared_task
from celery.exceptions import MaxRetriesExceededError
from django.db import transaction
from django.utils import timezone

from core.tracing import ensure_trace_id, set_trace_id

from .models import Payout
from .services import PaymentGateway, TemporaryPaymentError

logger = logging.getLogger("celery")
gateway = PaymentGateway()

MAX_RETRIES = int(os.environ["CELERY_MAX_RETRIES"])
RETRY_DELAY = int(os.environ["CELERY_RETRY_DELAY"])
PROCESSING_DELAY = int(os.environ["CELERY_PROCESSING_DELAY"])


@shared_task(bind=True, max_retries=MAX_RETRIES, default_retry_delay=RETRY_DELAY)
def process_payout(self, payout_id: int, trace_id: str = None):
    if trace_id:
        set_trace_id(trace_id)
    else:
        ensure_trace_id()

    with transaction.atomic():
        payout = Payout.objects.select_for_update().get(id=payout_id)

        if payout.status != Payout.Status.PENDING:
            logger.warning(f"Payout {payout.id} has invalid status: {payout.status}")
            return

        payout.status = Payout.Status.PROCESSING
        payout.save(update_fields=["status"])

    try:
        logger.info(f"Payout {payout.id}: starting payment")
        gateway.send_payment(
            user_id=payout.user_id,
            amount=payout.amount,
            currency=payout.currency,
            recipient_details=payout.recipient_details,
        )

        payout.status = Payout.Status.PROCESSED
        payout.processed_at = timezone.now()
        payout.save()

        logger.info(f"Payout {payout.id} processed successfully")

    except TemporaryPaymentError as exc:
        try:
            raise self.retry(exc=exc)
        except MaxRetriesExceededError:
            payout.status = Payout.Status.FAILED
            payout.save(update_fields=["status"])
            logger.error(f"Payout {payout.id} reached max retries, giving up")


@shared_task
def reconcile_processing_payouts():
    ensure_trace_id()
    timeout = timezone.now() - timedelta(seconds=PROCESSING_DELAY)

    stuck = Payout.objects.filter(status=Payout.Status.PROCESSING, updated_at__lt=timeout)

    for payout in stuck:
        payout.status = Payout.Status.FAILED
        payout.save(update_fields=["status"])
        logger.error("Payout stuck in PROCESSING", extra={"payout_id": payout.id})
