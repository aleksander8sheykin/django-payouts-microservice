from rest_framework import serializers

from .models import Payout


class PayoutSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, coerce_to_string=False)

    class Meta:
        model = Payout
        fields = [
            "id",
            "user_id",
            "amount",
            "payout_method",
            "payout_details",
            "status",
            "created_at",
            "processed_at",
        ]
        read_only_fields = ["id", "status", "created_at", "processed_at"]
