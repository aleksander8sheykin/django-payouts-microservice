from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView

from .views import healthcheck

urlpatterns = [
    path("healthz/", healthcheck, name="healthcheck"),
    path("api/payouts/", include("payouts.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
]
