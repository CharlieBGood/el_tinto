# Generated by Django 4.0.3 on 2022-09-06 03:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0009_alter_user_first_name_alter_user_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='best_user',
            field=models.BooleanField(default=False),
        ),
    ]
