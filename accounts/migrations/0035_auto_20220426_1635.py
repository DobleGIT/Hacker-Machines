# Generated by Django 2.2.12 on 2022-04-26 16:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0034_auto_20220426_1608'),
    ]

    operations = [
        migrations.RenameField(
            model_name='category',
            old_name='name',
            new_name='nombre',
        ),
    ]