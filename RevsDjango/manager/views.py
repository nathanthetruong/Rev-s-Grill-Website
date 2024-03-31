from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import MenuItems, Inventory
from django.db import connection
from datetime import datetime

# Create your views here.
def manager(request):
    # If we're adding an item, update the database
    if request.method == 'POST':
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')
        times_ordered = request.POST.get('times_ordered')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        # Get an available ID for a new menu_item
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT MAX(id) FROM menu_items")
            max_id = cursor.fetchone()[0]

        next_id = max_id + 1

        # Insert into the database
        with connection.cursor() as cursor:
            sql = "INSERT INTO menu_items (id, price, description, category, times_ordered, start_data, end_data) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, [next_id, price, description, category, times_ordered, start_date, end_date])

        return redirect('Revs-Manager-Screen')

    # We're not adding an item, so we just get it from our model
    else:
        menu_items = MenuItems.objects.all()
        inventory_items = Inventory.objects.all()
        context = {
            'menu_items': menu_items,
            'inventory_items': inventory_items,
        }
        return render(request, 'manager/manager.html', context)

def restock(request):
    return render(request, 'manager/restock.html')

def excess(request):
    return render(request, 'manager/excess.html')

def productusage(request):
    return render(request, 'manager/productusage.html')

def sales(request):
    return render(request, 'manager/sales.html')

def trends(request):
    return render(request, 'manager/trends.html')
