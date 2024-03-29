# Generated by Django 4.0.3 on 2022-04-16 21:00

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Mail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('html', models.TextField()),
                ('type', models.CharField(max_length=50)),
                ('created_by', models.CharField(max_length=50)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Mail',
                'verbose_name_plural': 'Mails',
            },
        ),
    ]
