import csv
from distutils.command.build_scripts import first_line_re

from el_tinto.users.models import User


def populate_users():
    with open('el_tinto/scripts/subscribed_members_export_2d07cc8628.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_counter = 0
        for row in csv_reader:
            if line_counter != 0:
                try:
                    user = User(
                        email=row[0],
                        first_name=row[1],
                        last_name=row[2],
                        is_staff=False,
                        is_superuser=False
                    )
                    user.save()
                except:
                    pass
            line_counter += 1
