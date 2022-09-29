import datetime
import os

from django.core.management.base import BaseCommand

from el_tinto.users.models import User
from el_tinto.mails.models import Mail, SentEmails


class Command(BaseCommand):
    help = 'Create referred users from input user. Used only for testing purpose'

    def add_arguments(self, parser):
        parser.add_argument('--email', dest='email', type=str)
        parser.add_argument('--referred_users', dest='referred_users', type=int)
        parser.add_argument('--run', dest='run', action='store_true', default=False)

    def handle(self, *args, **options):

        if os.getenv('DJANGO_CONFIGURATION') != 'Production':
            if not options.get('email', False):
                raise Exception('email is mandatory')

            if not options.get('referred_users', False):
                raise Exception('referred_users is mandatory')

            if options.get('run', False):

                try:
                    user = User.objects.get(email=options.get('email'))
                except User.DoesNotExist:
                    raise Exception(f'User with email {options.get("email")} does not exist in db')

                # Remove previous referred users
                User.objects.filter(referred_by=user).delete()

                referred_users_count = User.objects.filter(referred_by=user).count()

                if referred_users_count > 0:
                    raise Exception('An error occurred while deleting previous users')

                self.stdout.write('Previous users successfully deleted')

                mail = Mail.objects.last()

                if not mail:
                    mail = Mail.objects.create(subject='Ejemplo para el testeo')

                # create new users
                for i in range(options.get('referred_users')):
                    new_user = User.objects.create(
                        email=f'randomemail{str(i)}@ejemplo.com',
                        referred_by=user
                    )
                    SentEmails.objects.create(
                        mail=mail,
                        user=new_user,
                        opened_date=datetime.datetime.now()
                    )

                self.stdout.write(str(options.get('referred_users')) + ' new users created.')
                self.stdout.write('-- DONE --')
        else:
            raise Exception('Command only available in development and testing environments')
