# Generated by Django 2.2.12 on 2022-03-11 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0008_auto_20220311_1727'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='maquinas_completadas',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='alumno',
            name='puntos_conseguidos',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='alumno',
            name='root_flag',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='alumno',
            name='user_flag',
            field=models.IntegerField(null=True),
        ),
    ]
