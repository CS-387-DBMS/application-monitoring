# Generated by Django 3.2.13 on 2022-04-29 16:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('basic_input', '0004_rename_disk_usage_machine_packet_machine_port'),
    ]

    operations = [
        migrations.AddField(
            model_name='machine',
            name='passwrd',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
