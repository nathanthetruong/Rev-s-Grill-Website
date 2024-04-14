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
    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    startingDateForm = StartDateForm()
    endingDateForm = EndDateForm()
    if request.method == "POST":
        if "submit" in request.POST:
            startingDateForm = StartDateForm(request.POST)
            endingDateForm = EndDateForm(request.POST)

            # If the date is valid, extracts the selected date
            if startingDateForm.is_valid():
                startingDate = startingDateForm.cleaned_data['startDate']
            if endingDateForm.is_valid():
                endingDate = endingDateForm.cleaned_data['endDate']
            print(f"Received dates: Start - {startingDate}, End - {endingDate}")  

    excess_report = getExcessReport(startingDate, endingDate)
    #print(f"Query returned {len(excess_report)} items")  
    print(excess_report)

    # Default option
    context = {'excess_report': excess_report,
                'StartDateForm': startingDateForm,
                'EndDateForm': endingDateForm}

    return render(request, 'manager/excess.html', context)


def getExcessReport(startDate, endDate):
    with connection.cursor() as cursor:
        test_startDate = '2023-04-20'
        test_endDate = '2023-04-21'
        # Queries for available inventory items still below their quantity target between two dates
        sqlCommand = ("""
                        SELECT inv.id AS inventory_id, inv.description AS inventory_description, inv.quantity_target, COALESCE(SUM(fti.quantity), 0) AS quantity_consumed, inv.quantity_target * 0.1 AS ten_percent_target
                        FROM inventory inv
                        LEFT JOIN food_to_inventory fti ON inv.id = fti.inventory_id
                        LEFT JOIN menu_items mi ON fti.food_item_id = mi.id
                        LEFT JOIN order_breakout ob ON mi.id = ob.food_items
                        LEFT JOIN orders o ON ob.order_id = o.id 
                        WHERE o.order_time BETWEEN %s AND %s
                        GROUP BY inv.id, inv.description, inv.quantity_target
                        HAVING COALESCE(SUM(fti.quantity), 0) < inv.quantity_target * 0.1;                      
                      """)
        cursor.execute(sqlCommand, [startDate, endDate])
        cursorOutput = cursor.fetchall()

        """
        print("Executing SQL:", sqlCommand)
        print("With parameters:", startDate, endDate)
        print("Query Results:", cursorOutput)
        """

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[0])
        dataReport =[{'inventory_id': currentItem[0], 
                      'inventory_description': currentItem[1],
                      'quantity_target': currentItem[2],
                      'quantity_consumed': currentItem[3],
                      'ten_percent_target': currentItem[4]}
                       for currentItem in dataSorted]
        
        print(dataReport)
        return dataReport

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

        print("Executing SQL:", sqlCommand)
        print("With parameters:", startDate, endDate)
        print("Query Results:", cursorOutput)

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[0])
        dataReport =[{'id': currentItem[0], 'price': currentItem[1],
                       'description': currentItem[2], 'category': currentItem[3],
                       'total_quantity_ordered': currentItem[5]}
                       for currentItem in dataSorted]
        return dataReport

def trends(request):
    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    startingDateForm = StartDateForm()
    endingDateForm = EndDateForm()
    if request.method == "POST":
        if "submit" in request.POST:
            startingDateForm = StartDateForm(request.POST)
            endingDateForm = EndDateForm(request.POST)

            # If the date is valid, extracts the selected date
            if startingDateForm.is_valid():
                startingDate = startingDateForm.cleaned_data['startDate']
            if endingDateForm.is_valid():
                endingDate = endingDateForm.cleaned_data['endDate']
            print(f"Received dates: Start - {startingDate}, End - {endingDate}")  

    trends = getTrends(startingDate, endingDate)
    #print(f"Query returned {len(excess_report)} items")  
    print(trends)

    # Default option
    context = {'trends': trends,
               'StartDateForm': startingDateForm,
               'EndDateForm': endingDateForm}

    return render(request, 'manager/trends.html', context)

def getTrends(startDate, endDate):
    with connection.cursor() as cursor:
        # Queries for all items within the year
        sqlCommand = ("""
                    SELECT mi1.description AS Item1, mi2.description AS Item2, COUNT(*) AS Frequency 
                    FROM order_breakout ob1 
                    JOIN order_breakout ob2 ON ob1.order_id = ob2.order_id AND ob1.food_items < ob2.food_items 
                    JOIN menu_items mi1 ON ob1.food_items = mi1.id 
                    JOIN menu_items mi2 ON ob2.food_items = mi2.id 
                    JOIN orders o ON ob1.order_id = o.id 
                    WHERE o.order_time BETWEEN %s AND %s
                    GROUP BY mi1.description, mi2.description 
                    ORDER BY Frequency DESC;
                    """)
        cursor.execute(sqlCommand, [startDate, endDate])
        cursorOutput = cursor.fetchall()

        print("Executing SQL:", sqlCommand)
        print("With parameters:", startDate, endDate)
        print("Query Results:", cursorOutput)

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[2], reverse=True)
        dataReport =[{'item1': currentItem[0],
                      'item2': currentItem[1],
                      'frequency': currentItem[2]}
                       for currentItem in dataSorted]
        return dataReport
    
# Creates classes for date submissions
class StartDateForm(forms.Form):
    startDate = forms.DateField()

class EndDateForm(forms.Form):
    endDate = forms.DateField()
