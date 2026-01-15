import factory

from payouts.models import Payout


class PayoutFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Payout

    amount = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)
    status = Payout.Status.PENDING
    user_id = factory.Faker("pyint")
    payout_method = Payout.PayoutMethod.BANK_CARD
    payout_details = {"card": "0000 1111 2222 3333"}
