import logging

from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import generics

from core.tracing import get_trace_id

from .models import Payout
from .serializers import PayoutSerializer
from .tasks import process_payout

logger = logging.getLogger(__name__)


class PayoutCreateView(generics.CreateAPIView):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer

    @extend_schema(
        operation_id="createPayout",
        description="Создаём новую заявку на выплату и ставим её в очередь обработки",
        request=PayoutSerializer,
        responses={201: PayoutSerializer},
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value={
                    "user_id": 123,
                    "amount": 100.50,
                    "payout_method": "bank_card",
                    "payout_details": {"card": "0000 1111 2222 3333"},
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        payout_id = response.data.get("id")
        if payout_id:
            process_payout.delay(payout_id, get_trace_id())
        return response


class PayoutRetrieveView(generics.RetrieveAPIView):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer

    @extend_schema(
        operation_id="creategetPayoutPayout",
        description="Получаем статус заявки на выплату по ID",
        request=PayoutSerializer,
        responses={200: PayoutSerializer, 404: "Not Found"},
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value={
                    "id": 1,
                    "user_id": 123,
                    "amount": 100.50,
                    "payout_method": "bank_card",
                    "payout_details": {"card": "0000 1111 2222 3333"},
                    "status": "pending",
                    "created_at": "2026-01-14T12:00:00Z",
                    "processed_at": None,
                },
                request_only=True,
            ),
        ],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
