# Generated by Django 3.2.3 on 2021-09-27 00:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0023_auto_20210926_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='llaveregistro',
            name='subllaves',
        ),
        migrations.AddField(
            model_name='subllaveregistro',
            name='llave_padre_aleatoria',
            field=models.BooleanField(default=False),
        ),
    ]
