# Generated by Django 3.2.3 on 2021-09-14 04:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0018_auto_20210913_2322'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subllaveregistro',
            name='key',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.llaveregistro'),
        ),
    ]