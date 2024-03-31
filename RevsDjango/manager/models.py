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
    start_data = models.DateTimeField(blank=True, null=True)
    end_data = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'menu_items'