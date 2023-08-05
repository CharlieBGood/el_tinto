from datetime import datetime

import factory

from el_tinto.mails.models import Mail, SentEmails
from el_tinto.tests.tintos.factories import TintoFactory
from el_tinto.tests.users.factories import UserFactory


class DailyMailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mail

    subject = factory.Faker('sentence', nb_words=5)
    type = Mail.DAILY
    dispatch_date = datetime(2025, 2, 5, 6, 0)  # Make sure day is not sunday.
    tweet = factory.Faker('sentence', nb_words=5)
    subject_message = factory.Faker('sentence', nb_words=5)
    tinto = factory.SubFactory(TintoFactory)


class SundayMailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mail

    subject = factory.Faker('sentence', nb_words=5)
    type = Mail.SUNDAY
    dispatch_date = datetime(2025, 2, 9, 6, 0)  # Make sure day is sunday.
    tweet = factory.Faker('sentence', nb_words=5)
    subject_message = factory.Faker('sentence', nb_words=5)
    tinto = factory.SubFactory(TintoFactory)


class MilestoneMailFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Mail

    subject = factory.Faker('sentence', nb_words=5)
    type = Mail.MILESTONE


class SentEmailsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SentEmails

    mail = DailyMailFactory()
    user = UserFactory()
