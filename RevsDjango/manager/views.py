from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import MenuItems, Inventory
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
from django import forms

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
            sql = "INSERT INTO menu_items (id, price, description, category, times_ordered, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
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
    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    startingDateForm = StartDateForm()
    endingDateForm = EndDateForm()
    if request.method == "POST":
        if "submit_button" in request.POST:
            startingDateForm = StartDateForm(request.POST)
            endingDateForm = EndDateForm(request.POST)

            # If the date is valid, extracts the selected date
            if startingDateForm.is_valid():
                startingDate = startingDateForm.cleaned_data['startDate']
            if endingDateForm.is_valid():
                endingDate = endingDateForm.cleaned_data['endDate']

    sales_report = getSalesReport(startingDate, endingDate)

    # Default option
    context = {'sales_report': sales_report,
                'StartDateForm': startingDateForm,
                'EndDateForm': endingDateForm}

    return render(request, 'manager/sales.html', context)


def trends(request):
    return render(request, 'manager/trends.html')


# Function for getting the whole history of sales
# By default, gives the year
def getSalesReport(startDate, endDate=timezone.now().date()):
    with connection.cursor() as cursor:
        # Queries for all items within the year
        sqlCommand = ("SELECT menu_items.id, menu_items.price, menu_items.description, menu_items.category, " +
                        "menu_items.times_ordered, SUM(order_breakout.food_items) AS total_quantity_ordered " +
                        "FROM orders JOIN order_breakout ON orders.id = order_breakout.order_id JOIN menu_items " +
                        "ON order_breakout.food_items = menu_items.id WHERE orders.order_time BETWEEN %s AND %s " +
                        "GROUP BY menu_items.id, menu_items.description, menu_items.times_ordered, menu_items.price;")
        cursor.execute(sqlCommand, [startDate, endDate])
        cursorOutput = cursor.fetchall()

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[0])
        dataReport =[{'id': currentItem[0], 'price': currentItem[1],
                       'description': currentItem[2], 'category': currentItem[3],
                       'total_quantity_ordered': currentItem[5]}
                       for currentItem in dataSorted]
        
        return dataReport


# Creates classes for date submissions
class StartDateForm(forms.Form):
    startDate = forms.DateField()

class EndDateForm(forms.Form):
    endDate = forms.DateField()