from django.contrib.auth.models import Group
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import loaddata

from el_tinto.users.models import User


class Command(BaseCommand):
    help = "This sets up a development environment filling up all needed models."

    def add_arguments(self, parser):
        parser.add_argument("--email", dest="email", type=str)
        parser.add_argument("--password", dest="password", type=str)

    def handle(self, *args, **options):

        # Create groups
        Group.objects.get_or_create(name='Editor')
        founder_group, _ = Group.objects.get_or_create(name='Founder')

        # Set up admin user
        if options.get("email", False):
            if not options.get("password") or options.get("password") == "":
                raise CommandError("If you provide an email you also have to provide a password.")

            user, _ = User.objects.get_or_create(
                email=options.get("email"), is_staff=True, is_superuser=True
            )

            user.set_password(options.get("password"))

            user.save()

            founder_group.user_set.add(user)

        # Create needed models intances
        call_command(loaddata.Command(), "mails.json")
        call_command(loaddata.Command(), "templates.json")
        call_command(loaddata.Command(), "tinto_blocks_types.json")
        call_command(loaddata.Command(), "news_types.json")

        self.stdout.write(
            self.style.SUCCESS('Environment correctly set up.')
        )
