from django.db import models

# Create your models here.
class Inventory(models.Model):
    id = models.IntegerField(primary_key=True)
    description = models.TextField(blank=True, null=True)
    quantity_remaining = models.IntegerField(blank=True, null=True)
    quantity_target = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'inventory'

class MenuItems(models.Model):
    id = models.IntegerField(primary_key=True)
    price = models.FloatField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    times_ordered = models.IntegerField(blank=True, null=True)
    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu_items'

class Employees(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.TextField(blank=True, null=True)
    is_manager = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'employees'