from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import MenuItems, Inventory, Employees, Orders, Inventory
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from django import forms
from django.db import transaction
from django.contrib import messages


'''
This function will display the menu_items on the main manager page
It will also handle the ability to insert new menu items
'''
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
        context = {
            'menu_items': menu_items,
        }
        return render(request, 'manager/manager.html', context)

'''
This function will give us the ability to remove menu items from our database
'''
def deleteItem(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            with connection.cursor() as cursor:
                # First, delete the related entry from food_to_inventory
                cursor.execute("DELETE FROM food_to_inventory WHERE food_item_id = %s", [item_id])
                # Then, delete the item from menu_items
                cursor.execute("DELETE FROM menu_items WHERE id = %s", [item_id])

        return redirect('Revs-Manager-Screen')

'''
This function will give us the ability to modify menu items in our database
'''
def modifyItem(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')
        times_ordered = request.POST.get('times_ordered')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        menu_item = MenuItems.objects.get(id=item_id)
        menu_item.price = price
        menu_item.description = description
        menu_item.category = category
        menu_item.times_ordered = times_ordered
        menu_item.start_date = start_date
        menu_item.end_date = end_date
        menu_item.save()
    return redirect('Revs-Manager-Screen')

'''
This function will give us the ability to display the current list of staff
'''
def displayStaff(request):

    employees = Employees.objects.all()
    context = {
        'employees': employees,
    }

    return render(request, 'manager/staffmanagement.html', context)

'''
This function will give us the ability to modify the staff's properties
'''
def modifyStaff(request):
    if request.method == 'POST':
        employee_id = request.POST.get('id')
        name = request.POST.get('name')
        is_manager = request.POST.getlist('manager[]')
        email = request.POST.get('email')

        employee = Employees.objects.get(id=employee_id)
        employee.id = employee_id
        employee.name = name
        employee.email = email
        employee.is_manager = 'on' in is_manager
        employee.save()
    return redirect('Revs-staffmanagement-screen')

'''
This function will give us the ability to delete staff
'''
def deleteStaff(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            # Set employee_id to 0 in all related orders before deleting the employee, so the reports aren't affected
            Orders.objects.filter(employee_id=employee_id).update(employee_id=0)
            # Delete the employee
            Employees.objects.filter(id=employee_id).delete()

        return redirect('Revs-staffmanagement-screen')

'''
This function will give us the ability to add new staff
'''
def addStaff(request):
    if request.method == 'POST':
        employee_id = request.POST.get('new_id')
        name = request.POST.get('new_name')
        is_manager = request.POST.getlist('new_manager[]')

        # Check if the employee ID already exists
        if Employees.objects.filter(id=employee_id).exists():
            messages.error(request, 'Employee ID already in use. Please use a different ID.')
            return redirect('Revs-staffmanagement-screen')
        else:
            # Create new employee since ID is unique
            new_employee = Employees(id=employee_id, name=name, is_manager='on' in is_manager)
            new_employee.save()
            messages.success(request, 'New employee added successfully.')
            return redirect('Revs-staffmanagement-screen')
        
'''
This function will give us the ability to add new inventory items
'''
def addInventory(request):
    if request.method == 'POST':
        new_description = request.POST.get('new_description')
        new_quantity_remaining = request.POST.get('new_quantity_remaining')
        new_quantity_target = request.POST.get('new_quantity_target')

        # Get an available ID for a new inventory item
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM inventory")
            max_id = cursor.fetchone()[0]
        new_id = max_id + 1

        # Insert into the database
        with connection.cursor() as cursor:
            sql = "INSERT INTO inventory (id, description, quantity_remaining, quantity_target) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, [new_id, new_description, new_quantity_remaining, new_quantity_target])

        messages.success(request, 'New inventory item added successfully.')
        return redirect('Revs-restock-Screen')
    
'''
This function will give us the ability to remove inventory items
'''
def deleteInventory(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = Inventory.objects.get(id=item_id)
        item.delete()
        messages.success(request, 'Inventory item successfully deleted.')
        return redirect('Revs-restock-Screen')
    
'''
This function will give us the ability to modify inventory items
'''
def modifyInventory(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        description = request.POST.get('description')
        quantity_remaining = request.POST.get('quantity_remaining')
        quantity_target = request.POST.get('quantity_target')

        item = Inventory.objects.get(id=item_id)
        item.description = description
        item.quantity_remaining = quantity_remaining
        item.quantity_target = quantity_target
        item.save()
        messages.success(request, 'Inventory item successfully modified.')

        return redirect('Revs-restock-Screen')

def restock(request):
    with connection.cursor() as cursor:
        sqlCommand = ("""
                        SELECT id, description, quantity_remaining, quantity_target
                        FROM inventory
                      """)
        cursor.execute(sqlCommand)
        rows = cursor.fetchall()
        inventory_items = [
            {'id': row[0], 'description': row[1], 'quantity_remaining': row[2], 'quantity_target': row[3]}
            for row in rows
        ]
        context = {
            'inventory_items': inventory_items,
        }

        return render(request, 'manager/restock.html', context)

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

    excess_report = getExcessReport(startingDate, endingDate)

    # Default option
    context = {'excess_report': excess_report,
                'StartDateForm': startingDateForm,
                'EndDateForm': endingDateForm}

    return render(request, 'manager/excess.html', context)


def getExcessReport(startDate, endDate):
    with connection.cursor() as cursor:
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

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[0])
        dataReport =[{'inventory_id': currentItem[0], 
                      'inventory_description': currentItem[1],
                      'quantity_target': currentItem[2],
                      'quantity_consumed': currentItem[3],
                      'ten_percent_target': currentItem[4]}
                       for currentItem in dataSorted]
        
        return dataReport


# Creates the Product Usage Page
def productusage(request):
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

    product_usage_report = getProductUsageReport(startingDate, endingDate)

    # Default option
    context = {'product_usage_report': product_usage_report,
                'StartDateForm': startingDateForm,
                'EndDateForm': endingDateForm}

    return render(request, 'manager/productusage.html', context)


# Creates the Sales Report Page
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

# Function for getting the history of product usage
def getProductUsageReport(startDate, endDate):
    with connection.cursor() as cursor:
        # Queries for all items within the year
        sqlCommand = ("SELECT inventory.id AS inventory_id, inventory.description AS inventory_description, " +
                      "SUM(food_to_inventory.quantity) AS total_quantity_used FROM orders JOIN order_breakout " +
                      "ON orders.id = order_breakout.order_id JOIN food_to_inventory ON order_breakout.food_items " +
                      "= food_to_inventory.food_item_id JOIN inventory ON food_to_inventory.inventory_id = " +
                      "inventory.id WHERE orders.order_time BETWEEN %s AND %s GROUP BY inventory.id, " +
                      "inventory.description;")
        cursor.execute(sqlCommand, [startDate, endDate])
        cursorOutput = cursor.fetchall()

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[0])
        dataReport =[{'id': currentItem[0], 'description': currentItem[1], 'quantity': currentItem[2]
                      } for currentItem in dataSorted]
        
        return dataReport


# Function for getting the history of sales
def getSalesReport(startDate, endDate=timezone.now()):
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
        elif "submit2" in request.POST:
            # Get dates from POST request
            start_date_str = request.POST.get('startDate')
            end_date_str = request.POST.get('endDate')

            # Convert string dates to date objects
            startingDate = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            endingDate = datetime.strptime(end_date_str, '%Y-%m-%d').date()

    # Fetch real sales trends data
    sales_trends_data = getSalesTrendsData(startingDate, endingDate)
    monthly_growth_rates = getMonthlySalesData(startingDate, endingDate)

    trends = getTrends(startingDate, endingDate)

    # Default option
    context = {'trends': trends,
               'StartDateForm': startingDateForm,
               'EndDateForm': endingDateForm,
                'sales_trends_data': sales_trends_data,
                'monthly_growth_rates': monthly_growth_rates,
               }

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

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[2], reverse=True)
        dataReport =[{'item1': currentItem[0],
                      'item2': currentItem[1],
                      'frequency': currentItem[2]}
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

def orderManagement(request):
    return render(request, 'manager/ordermanagement.html')
    
# Creates classes for date submissions
class StartDateForm(forms.Form):
    startDate = forms.DateField()

class EndDateForm(forms.Form):
    endDate = forms.DateField()