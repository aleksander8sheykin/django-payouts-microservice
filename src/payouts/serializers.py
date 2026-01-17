from decimal import Decimal

from rest_framework import serializers

from .currency_choices import ISO_4217_CURRENCY_CHOICES
from .models import Payout


class PayoutSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(min_value=1)
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
        coerce_to_string=False,
    )
    currency = serializers.ChoiceField(choices=ISO_4217_CURRENCY_CHOICES)

    class Meta:
        model = Payout
        fields = [
            "id",
            "user_id",
            "amount",
            "currency",
            "recipient_details",
            "comment",
            "status",
            "created_at",
            "updated_at",
            "processed_at",
        ]
        read_only_fields = ["id", "status", "created_at", "updated_at", "processed_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Сумма выплаты должна быть положительной")
        return value


class PayoutPublicSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Payout
        fields = [
            "id",
            "user_id",
            "amount",
            "currency",
            "status",
            "created_at",
            "updated_at",
            "processed_at",
        ]


class PayoutStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = ["status"]

    def validate_status(self, value):
        allowed = {
            Payout.Status.PENDING,
            Payout.Status.PROCESSING,
            Payout.Status.PROCESSED,
            Payout.Status.FAILED,
        }
        if value not in allowed:
            raise serializers.ValidationError("Недопустимый статус")
        return value
