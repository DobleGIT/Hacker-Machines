# Generated by Django 2.2.12 on 2022-03-20 17:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_maquina_ip'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='profile_image',
            field=models.ImageField(default='foto_perfil.png', upload_to=''),
        ),
    ]