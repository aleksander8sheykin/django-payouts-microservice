from django.urls import path

from .views import PayoutListCreateView, PayoutRetrieveUpdateDeleteView

urlpatterns = [
    path("", PayoutListCreateView.as_view(), name="list-create-payouts"),
    path("<int:pk>/", PayoutRetrieveUpdateDeleteView.as_view(), name="payout-detail"),
]
