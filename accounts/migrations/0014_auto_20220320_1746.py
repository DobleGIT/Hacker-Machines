# Generated by Django 2.2.12 on 2022-03-20 17:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0013_auto_20220320_1745'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='profile_image',
            field=models.ImageField(default='foto_perfil.png', upload_to=''),
        ),
    ]
