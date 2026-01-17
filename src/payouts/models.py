from django.core.validators import MinValueValidator
from django.db import models

from .currency_choices import ISO_4217_CURRENCY_CHOICES


class Payout(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PROCESSING = "processing", "Processing"
        PROCESSED = "processed", "Processed"
        FAILED = "failed", "Failed"

    user_id = models.PositiveBigIntegerField(
        verbose_name="Ид пользователя",
        validators=[MinValueValidator(1)],
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма выплаты",
        validators=[MinValueValidator(0.01)],
    )

    currency = models.CharField(max_length=3, choices=ISO_4217_CURRENCY_CHOICES, verbose_name="Валюта")

    recipient_details = models.JSONField(verbose_name="Реквизиты получателя")

    comment = models.TextField(blank=True, verbose_name="Комментарий")

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name="Статус заявки"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата обработки")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user_id", "-created_at"], name="payout_user_created_idx"),
        ]

    def __str__(self):
        return f"Payout(id={self.id}, amount={self.amount} {self.currency}, status={self.status})"
