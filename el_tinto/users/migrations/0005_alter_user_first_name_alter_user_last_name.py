from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_unsuscribe'),
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

