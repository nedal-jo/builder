from django.db import models

class asset(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    mobile = models.IntegerField(blank=True, null=True)
    model = models.CharField(max_length=200, blank=True, null=True)
    date1 = models.DateField(blank=True, null=True)