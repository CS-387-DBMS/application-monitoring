# Generated by Django 4.0.4 on 2022-04-28 17:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('basic_input', '0002_alter_machine_machine_ip_alter_machine_machine_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='machine',
            old_name='cpu_threshold',
            new_name='CPU_usage',
        ),
        migrations.RenameField(
            model_name='machine',
            old_name='disk_threshold',
            new_name='Disk_usage',
        ),
        migrations.RenameField(
            model_name='machine',
            old_name='machine_ip',
            new_name='MachineIP',
        ),
        migrations.RenameField(
            model_name='machine',
            old_name='machine_name',
            new_name='MachineName',
        ),
        migrations.RenameField(
            model_name='machine',
            old_name='ram_threshold',
            new_name='RAM_usage',
        ),
    ]
