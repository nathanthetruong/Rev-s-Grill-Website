from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import MenuItems, Inventory
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
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
    startingDate = timezone.now().date() - timedelta(days=365)
    endingDate = timezone.now().date()

    if request.method == 'POST':
        # Get dates from POST request
        start_date_str = request.POST.get('startDate')
        end_date_str = request.POST.get('endDate')

        # Convert string dates to date objects
        startingDate = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        endingDate = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Fetch real sales trends data
    sales_trends_data = getSalesTrendsData(startingDate, endingDate)
    monthly_growth_rates = getMonthlySalesData(startingDate, endingDate)

    # Pass data to the template
    context = {
        'sales_trends_data': sales_trends_data,
        'monthly_growth_rates': monthly_growth_rates,

    }
    return render(request, 'manager/trends.html', context)

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
    
def getSalesTrendsData(startDate, endDate):
    with connection.cursor() as cursor:
        sqlCommand = """
        SELECT DATE(orders.order_time) AS order_date, SUM(menu_items.price * order_breakout.food_items) AS total_sales
        FROM orders 
        JOIN order_breakout ON orders.id = order_breakout.order_id 
        JOIN menu_items ON order_breakout.food_items = menu_items.id 
        WHERE orders.order_time BETWEEN %s AND %s 
        GROUP BY DATE(orders.order_time)
        ORDER BY DATE(orders.order_time);
        """
        cursor.execute(sqlCommand, [startDate, endDate])
        result = cursor.fetchall()

        # Convert query results into a list of dictionaries
        trends_data = [{'date': row[0], 'total_sales': row[1]} for row in result]
        return trends_data

def getMonthlySalesData(startDate, endDate):
    with connection.cursor() as cursor:
        sqlCommand = """
        SELECT DATE_TRUNC('month', orders.order_time) AS order_month, SUM(menu_items.price * order_breakout.food_items) AS monthly_sales
        FROM orders 
        JOIN order_breakout ON orders.id = order_breakout.order_id 
        JOIN menu_items ON order_breakout.food_items = menu_items.id 
        WHERE orders.order_time BETWEEN %s AND %s 
        GROUP BY DATE_TRUNC('month', orders.order_time)
        ORDER BY DATE_TRUNC('month', orders.order_time);
        """
        cursor.execute(sqlCommand, [startDate, endDate])
        result = cursor.fetchall()
        
        # Store monthly data in a dict for easy month-to-month comparison
        monthly_data = {}
        for row in result:
            # Convert date to first day of the month for uniformity
            month = row[0].strftime('%Y-%m')
            monthly_data[month] = row[1]
        
        # Calculate growth rates
        months_sorted = sorted(monthly_data.keys())
        monthly_growth_rates = []
        for i in range(1, len(months_sorted)):
            earlier_month = monthly_data[months_sorted[i-1]]
            later_month = monthly_data[months_sorted[i]]
            if earlier_month > 0:  # To avoid division by zero
                growth_rate = ((later_month - earlier_month) / earlier_month) * 100
            else:
                growth_rate = 0
            monthly_growth_rates.append((months_sorted[i], growth_rate))
        
        return monthly_growth_rates
    
# Creates classes for date submissions
class StartDateForm(forms.Form):
    startDate = forms.DateField()

class EndDateForm(forms.Form):
    endDate = forms.DateField()
