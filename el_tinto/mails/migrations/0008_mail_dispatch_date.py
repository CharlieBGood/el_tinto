# Generated by Django 4.0.3 on 2022-04-28 19:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0007_mail_version_alter_mail_created_by'),
    ]

    operations = [
        migrations.AddField(
            model_name='mail',
            name='dispatch_date',
            field=models.DateTimeField(null=True),
        ),
    ]
