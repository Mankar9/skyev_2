# Generated by Django 3.2.3 on 2021-09-09 23:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20210830_1859'),
    ]

    operations = [
        migrations.AddField(
            model_name='llaveregistro',
            name='archivo',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
