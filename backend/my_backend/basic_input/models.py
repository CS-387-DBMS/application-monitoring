from django.db import models

# Create your models here.
class Machine(models.Model):
    # Object { MachineName: "mn", MachineIP: "10", RAM_usage: 1, CPU_usage: 1, Disk_usage: 1 }
    MachineName = models.CharField(max_length=100, blank=True)
    MachineIP = models.CharField(max_length=100, blank=True)
    Port = models.IntegerField()
    RAM_usage = models.DecimalField(default=1.0, decimal_places=2, max_digits=3)
    CPU_usage = models.DecimalField(default=1.0, decimal_places=2, max_digits=3)
    packet = models.DecimalField(default=1.0, decimal_places=2, max_digits=3)

