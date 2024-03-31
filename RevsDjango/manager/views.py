from django.shortcuts import render
from django.http import HttpResponse
from .models import MenuItems, Inventory


# Create your views here.
def manager(request):
    menu_items = MenuItems.objects.all()
    inventory_items = Inventory.objects.all()
    context = {
        'menu_items': menu_items,
        'inventory_items': inventory_items,
    }
    return render(request, 'manager/manager.html', context)
