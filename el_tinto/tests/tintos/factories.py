import factory

from el_tinto.tintos.models import Tinto


class TintoFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tinto

    name = factory.Faker('sentence', nb_words=4)
    email_dispatch_date = factory.Faker('future_datetime', end_date='+5m')
