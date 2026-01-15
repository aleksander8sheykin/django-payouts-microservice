from django.db import models


class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    class PayoutMethod(models.TextChoices):
        BANK_CARD = "bank_card", "Bank card"
        SBP = "sbp", "SBP"

    user_id = models.BigIntegerField(verbose_name="Ид пользователя", db_index=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма выплаты")

    payout_method = models.CharField(max_length=32, choices=PayoutMethod.choices)

    payout_details = models.JSONField()

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Статус заявки"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата обработки")

    def __str__(self):
        return f"Payout(id={self.id}, amount={self.amount}, status={self.status})"
