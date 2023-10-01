import factory

from el_tinto.users.models import User, UserTier


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')


class EditorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.Faker('email')
    is_staff = True
    is_superuser = True


class UserTierFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = UserTier

    tier = UserTier.TIER_EXPORTATION_COFFEE
    user = factory.SubFactory(UserFactory)
    valid_to = factory.Faker('future_date')
