# Generated by Django 3.2.3 on 2021-08-07 17:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20210807_1243'),
    ]

    operations = [
        migrations.RenameField(
            model_name='usuario',
            old_name='cliente',
            new_name='empresa',
        ),
    ]