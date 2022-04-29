from django.db import models

# Create your models here.
class ChartData(models.Model):

    n = models.IntegerField(blank=True,default=0)