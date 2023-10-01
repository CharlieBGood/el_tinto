import csv
import io

from django.contrib import admin, messages
from django.forms import forms
from django.shortcuts import render

from el_tinto.mails.models import Mail
from el_tinto.users.models import User
from el_tinto.utils.users import create_user_referral_code
from el_tinto.utils.utils import UTILITY_MAILS, ONBOARDING_EMAIL_NAME


class SendMessageForm(forms.Form):
    csv_file = forms.FileField(label='Meta users csv')

@admin.action(description='Agregar usuarios de Meta')
def add_meta_users(_, request, queryset):
    """
    Add users from Meta csv file.

    :params:
    request: Request object

    """
    if 'add' not in request.POST:
        return render(request, 'admin/add_meta_users_form.html')

    form = SendMessageForm(request.POST, request.FILES)

    if not form.is_valid():
        messages.error(request, 'Form is not valid.')
        return

    csv_file = request.FILES['csv_file']

    # Read csv file InMemoryUploadedFile
    file = csv_file.read().decode('utf-16')
    reader = csv.DictReader(io.StringIO(file), delimiter="\t")

    for line in reader:
        try:
            user = User.objects.get(email=line['email'])

            # Activate users
            if not user.is_active:
                user.is_active = True
                user.save()

        # Create new user in case it doesn't exist
        except User.DoesNotExist:
            user = User.objects.create(
                email=line['email'],
                first_name=line['first_name'],
                last_name=line['last_name'],
                utm_source=User.FACEBOOK,
                medium='ads'
            )

            user.referral_code = create_user_referral_code(user)
            user.save()

            onboarding_mail_instance = Mail.objects.get(id=UTILITY_MAILS.get(ONBOARDING_EMAIL_NAME))
            mail = onboarding_mail_instance.get_mail_class()
            mail.send_mail(user)
