# Generated by Django 4.0.3 on 2022-09-13 14:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0010_user_best_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='best_user',
        ),
    ]