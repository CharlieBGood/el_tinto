# Generated by Django 4.0.3 on 2022-08-31 23:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_merge_20220815_2036'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='first_name',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
        migrations.AlterField(
            model_name='user',
            name='last_name',
            field=models.CharField(blank=True, default='', max_length=25),
        ),
    ]