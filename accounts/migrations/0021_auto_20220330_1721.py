# Generated by Django 2.2.12 on 2022-03-30 17:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_auto_20220330_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alumno',
            name='accessed_machines',
        ),
        migrations.AlterField(
            model_name='acceso',
            name='alumnoA',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]