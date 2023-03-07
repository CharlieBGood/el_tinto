import csv

from el_tinto.users.models import User

def update_best_users():

    User.objects.all().update(best_user=False)

    with open('el_tinto/scripts/grupos_taller.csv') as file:

        csvreader = csv.reader(file)

        # Dismiss headers
        next(csvreader)

        for row in csvreader:
            user = User.objects.filter(email=row[1]).first()

            if user:
                user.best_user = True
                user.first_name = row[0]
                user.size_group = row[2]
                user.i = row[3]
                user.group = row[4]
                user.invite = f"<a>{row[5]}</a>"
                user.date_time = row[6]
                user.save()
