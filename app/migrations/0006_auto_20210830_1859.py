# Generated by Django 3.2.3 on 2021-08-31 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0005_cliente_max_casos'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='prefetch',
            name='finalizado',
        ),
        migrations.RemoveField(
            model_name='prefetch',
            name='ruta',
        ),
        migrations.AddField(
            model_name='prefetch',
            name='exe_file',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='last_run_time',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='pf_file',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='pf_hash',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='pf_run_count',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='pf_version',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='volume_count',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='volume_dev_path',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='volume_serial_number',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='prefetch',
            name='volume_timestamp',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='evidencia',
            name='archivo',
            field=models.FileField(blank=True, null=True, upload_to='evidencia'),
        ),
    ]
