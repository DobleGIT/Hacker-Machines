# Generated by Django 2.2.12 on 2022-04-27 17:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0041_auto_20220427_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquina',
            name='dificultad',
            field=models.CharField(choices=[('Fácil', 'Fácil'), ('Media', 'Media'), ('Difícil', 'Difífil'), ('Insana', 'Insana')], max_length=30, null=True),
        ),
    ]
