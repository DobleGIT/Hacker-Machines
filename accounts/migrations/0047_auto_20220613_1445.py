# Generated by Django 2.2.12 on 2022-06-13 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0046_maquina_activa'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maquina',
            name='activa',
        ),
        migrations.AddField(
            model_name='maquina',
            name='reboot',
            field=models.DateTimeField(null=True),
        ),
    ]