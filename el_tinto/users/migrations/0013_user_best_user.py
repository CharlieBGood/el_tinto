# Generated by Django 4.0.3 on 2023-03-01 22:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0012_user_referral_code_user_referred_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='best_user',
            field=models.BooleanField(default=False),
        ),
    ]
