# Generated by Django 2.2.12 on 2022-04-12 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0030_auto_20220406_1058'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alumno',
            name='openvpnFile',
            field=models.FileField(null=True, upload_to='openvpn/'),
        ),
    ]
