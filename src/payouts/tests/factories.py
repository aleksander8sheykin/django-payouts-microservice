from decimal import Decimal

import factory

from payouts.models import Payout


class PayoutFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payout

    amount = Decimal("150.75")
    status = Payout.Status.PENDING
    user_id = factory.Faker("pyint")
    currency = "RUB"
    recipient_details = {"card": "0000 1111 2222 3333"}
    comment = ""
