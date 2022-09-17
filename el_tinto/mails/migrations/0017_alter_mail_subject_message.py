# Generated by Django 4.0.3 on 2022-09-13 15:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mails', '0016_mail_subject_message'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mail',
            name='subject_message',
            field=models.CharField(blank=True, default='', help_text='Texto que acompaña al subject', max_length=128),
        ),
    ]
