import csv

from el_tinto.users.models import User

def update_best_users():
    with open('el_tinto/scripts/user_interviews.csv') as file:

        csvreader = csv.reader(file)

        # Dismiss headers
        next(csvreader)

        for row in csvreader:
            user = User.objects.filter(email=row[1]).first()

            if user:
                user.best_user = True
                user.save()
