# Generated by Django 2.2.12 on 2022-04-27 17:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0039_auto_20220427_1726'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquina',
            name='dificultad',
            field=models.CharField(choices=[('FACIL', 'Facil'), ('MEDIA', 'Media'), ('DIFICIL', 'Difífil'), ('INSANA', 'Insana')], max_length=30, null=True),
        ),
    ]
