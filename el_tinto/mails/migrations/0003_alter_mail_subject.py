# Generated by Django 4.0.3 on 2022-04-16 21:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0002_mail_subject'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='subject',
            field=models.CharField(default='', max_length=256),
        ),
    ]
