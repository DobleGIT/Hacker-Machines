# Generated by Django 2.2.12 on 2022-03-28 15:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0016_auto_20220328_1524'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maquina',
            name='profile_image',
            field=models.ImageField(default='linuxLogo.png', upload_to=''),
        ),
    ]