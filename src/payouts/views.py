import logging

from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiTypes, extend_schema
from rest_framework import generics
from rest_framework.response import Response

from core.tracing import get_trace_id

from .models import Payout
from .pagination import PayoutsPagination
from .serializers import (
    PayoutPublicSerializer,
    PayoutSerializer,
    PayoutStatusUpdateSerializer,
)
from .tasks import process_payout

logger = logging.getLogger(__name__)


class PayoutListCreateView(generics.ListCreateAPIView):
    queryset = Payout.objects.all().order_by("-created_at")
    serializer_class = PayoutSerializer
    pagination_class = PayoutsPagination

    @extend_schema(
        operation_id="listPayouts",
        description="Список заявок на выплату (без чувствительных данных)",
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Идентификатор пользователя. Без него список пуст.",
            ),
        ],
        responses={200: PayoutPublicSerializer(many=True)},
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user_id")
        if not user_id:
            return queryset.none()
        try:
            user_id_value = int(user_id)
        except (TypeError, ValueError):
            return queryset.none()
        return queryset.filter(user_id=user_id_value)

    @extend_schema(
        operation_id="createPayout",
        description="Создаём новую заявку на выплату и ставим её в очередь обработки",
        request=PayoutSerializer,
        responses={201: PayoutPublicSerializer},
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value={
                    "user_id": 123,
                    "amount": 100.50,
                    "currency": "RUB",
                    "recipient_details": {"card": "0000 1111 2222 3333"},
                    "comment": "Оплата бонуса",
                },
                request_only=True,
            ),
        ],
    )
    def perform_create(self, serializer):
        payout = serializer.save()
        process_payout.apply_async(
            args=(payout.id,),
            kwargs={"trace_id": get_trace_id()},
        )

    def create(self, request, *args, **kwargs):
        logger.info("Create payout request received")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            PayoutPublicSerializer(serializer.instance).data,
            status=201,
            headers=headers,
        )

    def get_serializer_class(self):
        if self.request.method == "GET":
            return PayoutPublicSerializer
        return PayoutSerializer


class PayoutRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Payout.objects.all()
    serializer_class = PayoutSerializer
    http_method_names = ["get", "patch", "delete"]

    @extend_schema(
        operation_id="getPayout",
        description="Получаем статус заявки на выплату по ID",
        request=PayoutSerializer,
        responses={200: PayoutPublicSerializer, 404: "Not Found"},
        examples=[
            OpenApiExample(
                name="Пример запроса",
                value={
                    "id": 1,
                    "user_id": 123,
                    "amount": 100.50,
                    "currency": "RUB",
                    "recipient_details": {"card": "0000 1111 2222 3333"},
                    "comment": "Оплата бонуса",
                    "status": "pending",
                    "created_at": "2026-01-14T12:00:00Z",
                    "updated_at": "2026-01-14T12:05:00Z",
                    "processed_at": None,
                },
                request_only=True,
            ),
        ],
    )
    @extend_schema(
        operation_id="updatePayoutStatus",
        description="Частично обновляем заявку (только статус)",
        request=PayoutStatusUpdateSerializer,
        responses={200: PayoutPublicSerializer},
    )
    def patch(self, request, *args, **kwargs):
        logger.info("Patch payout request received")
        super().patch(request, *args, **kwargs)
        payout = self.get_object()
        return Response(PayoutPublicSerializer(payout).data)

    @extend_schema(
        operation_id="deletePayout",
        description="Удаляем заявку на выплату",
        responses={204: None},
    )
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return PayoutStatusUpdateSerializer
        if self.request.method == "GET":
            return PayoutPublicSerializer
        return PayoutSerializer
