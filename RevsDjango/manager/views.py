from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import MenuItems, Inventory, Employees, Orders, Inventory
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta, date
from django.contrib import messages
import os
from django.conf import settings

def manager(request):
    # If we're adding an item, update the database
    if request.method == 'POST':
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')
        times_ordered = request.POST.get('times_ordered')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        image = request.FILES.get('image')

        # validates the dates when adding menu items
        if end_date < start_date:
            messages.error(request, "End date must be after start date")

            return redirect('Revs-Manager-Screen')

        # Get an available ID for a new menu_item
        with connection.cursor() as cursor:
            
            cursor.execute("SELECT MAX(id) FROM menu_items")
            max_id = cursor.fetchone()[0]

        next_id = max_id + 1

        # Insert into the database
        with connection.cursor() as cursor:
            sql = "INSERT INTO menu_items (id, price, description, category, times_ordered, start_date, end_date) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, [next_id, price, description, category, times_ordered, start_date, end_date])

        if image:
            # Write to the orders static images in orders
            save_path = os.path.join(settings.BASE_DIR, 'orders/static', description + ".jpeg")
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            
            with open(save_path, 'wb+') as destination:
                for chunk in image.chunks():
                    destination.write(chunk)


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
        startDate = request.POST.get('startDate')
        endDate = request.POST.get('endDate')

        menu_item = MenuItems.objects.get(id=item_id)
        menu_item.price = price
        menu_item.description = description
        menu_item.category = category
        menu_item.times_ordered = times_ordered
        menu_item.start_date = startDate
        menu_item.end_date = endDate
        menu_item.save()
    return redirect('Revs-Manager-Screen')

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
        return redirect('Revs-inventory-Screen')
    
'''
This function will give us the ability to remove inventory items
'''
def deleteInventory(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = Inventory.objects.get(id=item_id)
        item.delete()
        messages.success(request, 'Inventory item successfully deleted.')
        return redirect('Revs-inventory-Screen')
    
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

        return redirect('Revs-inventory-Screen')


def inventory(request):
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

        return render(request, 'manager/inventory.html', context)

def restocking(request):
    with connection.cursor() as cursor:
        sqlCommand = ("""
                        SELECT id, description, quantity_remaining, quantity_target
                        FROM inventory WHERE quantity_remaining < quantity_target
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

        return render(request, 'manager/restocking.html', context)

def excess(request):
    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

    excessReport = getExcessReport(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']
    context = {'report': excessReport}

    return render(request, 'manager/excess.html', context)


# Creates the Product Usage Page
def productusage(request):
    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

    productUsageReport = getProductUsageReport(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']

    context = {'report': productUsageReport}

    return render(request, 'manager/productusage.html', context)


# Creates the Sales Report Page
def sales(request):
    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

    salesReport = getSalesReport(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']

    context = {'report': salesReport}

    return render(request, 'manager/sales.html', context)


def trends(request):
    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

    '''
    # Fetch real sales trends data
    sales_trends_data = getSalesTrendsData(request, startingDate, endingDate)
    monthly_growth_rates = getMonthlySalesData(request, startingDate, endingDate)
    '''

    trends = getTrends(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']

    # Default option
    context = {'report': trends}

    return render(request, 'manager/trends.html', context)


# Validates date inputs
def validateDate(startDate, endDate):
    minimumDate = date(2023, 1, 1)
    maximumDate = date(2030, 1, 1)
    if startDate >= endDate:
        return False, "End Date should be after the Start Date"
    if startDate < minimumDate or endDate < minimumDate:
        return False, "Don't input anything lower than 01/01/2023"
    if startDate > maximumDate or endDate > maximumDate:
        return False, "Don't input anything higher than 01/01/2030"
    return True, "No error"


def getExcessReport(request, startDate, endDate):
    with connection.cursor() as cursor:
        # Queries for available inventory items still below their quantity target between two dates
        sqlCommand = ("""
                        SELECT inv.id AS inventory_id, inv.description AS inventory_description,
                        inv.quantity_target, COALESCE(SUM(fti.quantity), 0) AS quantity_consumed,
                        CAST(inv.quantity_target AS FLOAT) * 0.1 AS ten_percent_target
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
        dataReport =[{'id': currentItem[0], 
                      'description': currentItem[1],
                      'target_quantity': currentItem[2],
                      'quantity_consumed': currentItem[3],
                      'ten_percent_target': float(currentItem[4])}
                       for currentItem in dataSorted]
        request.session['currentReport'] = dataReport
        
        return dataReport


# Function for getting the history of product usage
def getProductUsageReport(request, startDate, endDate):
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
        request.session['currentReport'] = dataReport

        return dataReport


# Function for getting the history of sales
def getSalesReport(request, startDate, endDate=timezone.now()):
    with connection.cursor() as cursor:
        # Queries for all items within the year
        sqlCommand = ("""
                        SELECT mi.id, mi.price, mi.description, mi.category, COUNT(ob.food_items) AS total_quantity_ordered, mi.price * COUNT(ob.food_items) AS revenue
                        FROM orders o
                        JOIN order_breakout ob ON o.id = ob.order_id
                        JOIN menu_items mi ON ob.food_items = mi.id
                        WHERE o.order_time BETWEEN %s AND %s
                        GROUP BY mi.id, mi.price, mi.description, mi.category
                        ORDER BY revenue DESC;
                      """)
        cursor.execute(sqlCommand, [startDate, endDate])
        cursorOutput = cursor.fetchall()

        # Sorts and places all the items into the context
        dataSorted = sorted(cursorOutput, key=lambda x: x[0])
        dataReport =[{'id': currentItem[0], 'price': currentItem[1],
                       'description': currentItem[2], 'category': currentItem[3],
                       'totalQuantityOrdered': currentItem[4], 'revenue': currentItem[5]}
                       for currentItem in dataSorted]
        request.session['currentReport'] = dataReport

        return dataReport


def getTrends(request, startDate, endDate):
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
        request.session['currentReport'] = dataReport

        return dataReport

'''
def getSalesTrendsData(request, startDate, endDate):
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
        dataReport = [{'date': row[0], 'total_sales': row[1]} for row in result]

        return dataReport

def getMonthlySalesData(request, startDate, endDate):
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
'''

def orderManagement(request):
    context = {}
    if request.method == 'POST':
        if 'submit_date' in request.POST:
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            orders = Orders.objects.filter(order_time__date__range=[startDate, endDate])
        elif 'submit_id' in request.POST:
            order_id = request.POST.get('orderID')
            orders = [Orders.objects.get(id=order_id)]
        elif 'complete_order' in request.POST:
            order_id = request.POST.get('complete_order')
            order = Orders.objects.get(id=order_id)
            order.status = 'Complete'
            order.save()
            return redirect('Revs-ordermanagement')
        elif 'cancel_order' in request.POST:
            order_id = request.POST.get('cancel_order')
            order = Orders.objects.get(id=order_id)
            order.status = 'Cancelled'
            order.save()
            return redirect('Revs-ordermanagement')
        # Get menu items associated with each order
        context['orders'] = orders
        for order in orders:
            order.items = getOrderItems(order.id)
    else:
        orders = Orders.objects.filter(status='In Progress')
         # Get menu items associated with each order
        context['orders'] = orders
        for order in orders:
            order.items = getOrderItems(order.id)

    return render(request, 'manager/ordermanagement.html', context)

'''
This function will get all the menu items associated with a specific order id
'''
def getOrderItems(order_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT mi.description
            FROM orders o
            JOIN order_breakout ob ON o.id = ob.order_id
            JOIN menu_items mi ON ob.food_items = mi.id
            WHERE o.id = %s
        """, [order_id])
        items = cursor.fetchall()
    return [item[0] for item in items]

def popularity(request):
    startingDate = timezone.now().date() - timedelta(days=365)
    endingDate = timezone.now().date()
    item_limit = 10 

    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')
        item_limit = request.POST.get('item_limit', '10')

    popularityReport = getPopularityData(request, startingDate, endingDate, item_limit)
    context = {
        'report': popularityReport,
        'startDate': startingDate,
        'endDate': endingDate
    }

    return render(request, 'manager/popularity.html', context)

def getPopularityData(request, startDate, endDate, limit):
    with connection.cursor() as cursor:
        sqlCommand = """
                    SELECT mi.id, mi.description, COUNT(ob.order_id) AS times_ordered
                    FROM menu_items mi
                    JOIN order_breakout ob ON mi.id = ob.food_items
                    JOIN orders o ON ob.order_id = o.id
                    WHERE o.order_time BETWEEN %s AND %s
                    GROUP BY mi.id, mi.description
                    ORDER BY times_ordered DESC
                    LIMIT %s;
                    """
        cursor.execute(sqlCommand, [startDate, endDate, limit])
        cursorOutput = cursor.fetchall()

        # Sorts and places all the items into the context
        dataReport = [{'id': item[0], 'description': item[1], 'times_ordered': item[2]} for item in cursorOutput]

        request.session['currentReport'] = dataReport

        return dataReport

# Sort function for tables
def sortTable(request):
    sortField = request.GET.get('sortField', 'description')
    tableName = request.GET.get('tableName', 'sales')

    # Handles tracking previous search fields and tables
    previousField = ""
    if 'currentField' in request.session:
        previousField = request.session.get('currentField')
    request.session['currentField'] = sortField

    previousTable = ""
    if 'currentTable' in request.session:
        previousTable = request.session.get('currentTable')
    request.session['currentTable'] = tableName

    # Sorts the data in the table and checks for order reversal
    currentReport = request.session.get('currentReport')
    if sortField == previousField and tableName == previousTable:
        currentReport.reverse()
    else:
        currentReport = sorted(currentReport, key=lambda x: x[sortField])
    request.session['currentReport'] = currentReport

    context = {
        'report': currentReport
    }

    return render(request, f'manager/{tableName}.html', context)