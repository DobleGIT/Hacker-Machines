# Generated by Django 2.2.12 on 2022-05-01 10:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0042_auto_20220427_1732'),
    ]

    operations = [
        migrations.AddField(
            model_name='acceso',
            name='finished_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]