# Generated by Django 2.2.12 on 2022-03-10 18:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('accounts', '0005_auto_20220303_1723'),
    ]

    operations = [
        migrations.CreateModel(
            name='Alumno',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('maquinas_completadas', models.IntegerField()),
                ('puntos_conseguidos', models.IntegerField()),
                ('user_flag', models.IntegerField()),
                ('root_flag', models.IntegerField()),
                ('user', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.RemoveField(
            model_name='maquina',
            name='nombre_creador',
        ),
        migrations.DeleteModel(
            name='Usuario',
        ),
    ]
