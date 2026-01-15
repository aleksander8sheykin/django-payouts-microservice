from django.urls import path

from .views import PayoutCreateView, PayoutRetrieveView

urlpatterns = [
    path("", PayoutCreateView.as_view(), name="create-payout"),
    path("<int:pk>/", PayoutRetrieveView.as_view(), name="get-payout"),
]
