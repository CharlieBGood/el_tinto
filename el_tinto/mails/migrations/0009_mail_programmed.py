# Generated by Django 4.0.3 on 2022-04-30 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0008_mail_dispatch_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='programmed',
            field=models.BooleanField(default=False),
        ),
    ]