# Generated by Django 3.2.3 on 2021-10-02 04:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0026_llaveregistro_nombre_subllaves'),
    ]

    operations = [
        migrations.CreateModel(
            name='EstadoEvidencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(blank=True, max_length=10, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='evidencia',
            name='estado',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='app.estadoevidencia'),
        ),
    ]
