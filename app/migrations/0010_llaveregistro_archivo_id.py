# Generated by Django 3.2.3 on 2021-09-14 02:54

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_archivoregistro'),
    ]

    operations = [
        migrations.AddField(
            model_name='llaveregistro',
            name='archivo_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.archivoregistro'),
            preserve_default=False,
        ),
    ]