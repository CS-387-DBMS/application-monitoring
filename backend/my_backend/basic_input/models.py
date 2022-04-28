from django.db import models

# Create your models here.
class Machine(models.Model):
    machine_name = models.CharField(max_length=100, blank=True, default='')
    machine_ip = models.CharField(max_length=100, blank=True, default='')
    ram_threshold = models.DecimalField(default=1.0, decimal_places=2, max_digits=3)
    cpu_threshold = models.DecimalField(default=1.0, decimal_places=2, max_digits=3)
    disk_threshold = models.DecimalField(default=1.0, decimal_places=2, max_digits=3)