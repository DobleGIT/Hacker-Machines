# Generated by Django 2.2.12 on 2022-06-13 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0047_auto_20220613_1445'),
    ]

    operations = [
        migrations.AddField(
            model_name='maquina',
            name='activa',
            field=models.BooleanField(default=True),
        ),
    ]
