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
    """
    Manage restaurant menu items by adding, modifying, and deleting items.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing metadata and user information.

    Returns:
        HttpResponse: Redirects to different views based on user actions and permissions or renders the manager.html template with menu items data.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')


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
        if validateDate(request, start_date, end_date) == False:
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

        messages.success(request, 'Menu item successfully added.')

        return redirect('Revs-Manager-Screen')

    # We're not adding an item, so we just get it from our model
    else:
        menu_items = MenuItems.objects.all()
        context = {
            'menu_items': menu_items,
        }
        return render(request, 'manager/manager.html', context)

def deleteItem(request):
    """
    Deletes a menu item from the database based on the item ID provided through the POST request.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing the menu item ID to delete.

    Returns:
        HttpResponse: Redirects to the manager screen after deleting the item.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        if item_id:
            with connection.cursor() as cursor:
                # First, delete the related entry from food_to_inventory
                cursor.execute("DELETE FROM food_to_inventory WHERE food_item_id = %s", [item_id])
                # Then, delete the item from menu_items
                cursor.execute("DELETE FROM menu_items WHERE id = %s", [item_id])

        messages.success(request, 'Menu item successfully deleted.')

        return redirect('Revs-Manager-Screen')

def modifyItem(request):
    """
    Modifies details of an existing menu item based on form data received through a POST request.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing updated data for the menu item.

    Returns:
        HttpResponse: Redirects to the manager screen after updating the item.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        price = request.POST.get('price')
        description = request.POST.get('description')
        category = request.POST.get('category')
        times_ordered = request.POST.get('times_ordered')
        startDate = request.POST.get('start_date')
        endDate = request.POST.get('end_date')

        # validates the dates when modifying menu items
        if validateDate(request, startDate, endDate) == False:
            return redirect('Revs-Manager-Screen')

        menu_item = MenuItems.objects.get(id=item_id)
        menu_item.price = price
        menu_item.description = description
        menu_item.category = category
        menu_item.times_ordered = times_ordered
        menu_item.start_date = startDate
        menu_item.end_date = endDate
        menu_item.save()

        messages.success(request, 'Menu item successfully modified.')

    return redirect('Revs-Manager-Screen')

def addInventory(request):
    """
    Adds a new inventory item to the database using data from a POST request.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing new inventory item details.

    Returns:
        HttpResponse: Redirects to the inventory management screen with a success message.
    """
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
    
def deleteInventory(request):
    """
    Deletes an inventory item from the database using the item ID from a POST request.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing the inventory item ID to delete.

    Returns:
        HttpResponse: Redirects to the inventory management screen with a success message.
    """
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        item = Inventory.objects.get(id=item_id)
        item.delete()
        messages.success(request, 'Inventory item successfully deleted.')
        return redirect('Revs-inventory-Screen')
    
def modifyInventory(request):
    """
    Modifies details of an existing inventory item based on form data received through a POST request.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing updated data for the inventory item.

    Returns:
        HttpResponse: Redirects to the inventory management screen with a success message.
    """
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
    """
    Displays current inventory items and their details.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the inventory.html template with inventory items data.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

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
    """
    Provides a view for items that need restocking based on their current quantity versus target quantity.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the restocking.html template with items needing restocking.
    """

    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

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
    """
    Displays items that have not met expected usage over a specified date range, helping identify excess inventory.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the excess.html template with items considered excess.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

        # validate dates
        if validateDate(request, startingDate, endingDate) == False:
            return redirect('Revs-excess-Screen')


    excessReport = getExcessReport(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']
    context = {'report': excessReport}

    return render(request, 'manager/excess.html', context)


# Creates the Product Usage Page
def productusage(request):
    """
    Generates a report on the usage of products over a specified date range.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the productusage.html template with product usage data.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

        # validate dates
        if validateDate(request, startingDate, endingDate) == False:
            return redirect('Revs-productusage-Screen')

    productUsageReport = getProductUsageReport(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']

    context = {'report': productUsageReport}

    return render(request, 'manager/productusage.html', context)


# Creates the Sales Report Page
def sales(request):
    """
    Generates a sales report detailing the quantity ordered and revenue generated for each menu item over a specified date range.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the sales.html template with sales data.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

        # validate dates
        if validateDate(request, startingDate, endingDate) == False:
            return redirect('Revs-sales-Screen')

    salesReport = getSalesReport(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']

    context = {'report': salesReport}

    return render(request, 'manager/sales.html', context)


def trends(request):
    """
    Analyzes ordering trends to identify frequently ordered together items over a specified date range from the POST request.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the trends.html template with trend data.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

    startingDate = timezone.now().date()-timedelta(days=365)
    endingDate = timezone.now().date()
    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')

        # validate dates
        if validateDate(request, startingDate, endingDate) == False:
            return redirect('Revs-trends-Screen')

    trends = getTrends(request, startingDate, endingDate)
    if 'currentField' in request.session:
        del request.session['currentField']

    # Default option
    context = {'report': trends}

    return render(request, 'manager/trends.html', context)


# Validates date inputs
def validateDate(request, startDate, endDate):
    """
    Examines the inputs and determines if they are valid dates for Rev's Grill

    Args:
        startDate (date): Inputted start date.
        endDate (date): Inputted end date.

    Returns:
        bool: A bool of whether the dates were valid or not.
    """

    # Convert string dates to datetime.date objects
    try:
        startDate = datetime.strptime(startDate, '%Y-%m-%d').date()
        endDate = datetime.strptime(endDate, '%Y-%m-%d').date()
    except ValueError:
        messages.error(request, 'Invalid date format. Please use YYYY-MM-DD format.')
        return False

    # Compare with our set dates
    minimumDate = date(2023, 1, 1)
    maximumDate = date(2999, 1, 1)
    if startDate >= endDate:
        messages.error(request, 'The End Date should be after the Start Date.')
        return False
    if startDate < minimumDate or endDate < minimumDate:
        messages.error(request, "You may not input a date before Rev's Grill was created (01/01/2023)")
        return False
    if startDate > maximumDate or endDate > maximumDate:
        messages.error(request, "You may not input anything higher than 01/01/2999")
        return False
    return True


def getExcessReport(request, startDate, endDate):
    """
    Retrieves a report detailing inventory items that have consumption below 10% of their target quantity between two dates.
    The function queries the database to identify the inventory items and calculates their consumption as a percentage of the target.

    Args:
        request (HttpRequest): The HTTP request object.
        startDate (date): The start date for the report period.
        endDate (date): The end date for the report period.

    Returns:
        list[dict]: A list of dictionaries where each dictionary represents an inventory item that is below 10% of their target quantity between two dates.
    """
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
    """
    Generates a detailed report on the usage of inventory items between two dates.
    The function queries the database to sum up the total quantity used from inventory across all orders within the specified date range.

    Args:
        request (HttpRequest): The HTTP request object.
        startDate (date): The start date for the report period.
        endDate (date): The end date for the report period.

    Returns:
        list[dict]: A list of dictionaries with each dictionary containing details of inventory usage such as item ID, description, and quantity used.
    """
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
    """
    Produces a sales report for menu items showing the quantity ordered and the total revenue generated within a specified date range.
    The function queries the database for all orders placed between the start and end dates, aggregating data by menu item.

    Args:
        request (HttpRequest): The HTTP request object.
        startDate (date): The start date for the report period.
        endDate (date): The end date for the report period.

    Returns:
        list[dict]: A list of dictionaries, each containing details of sales for a specific menu item including ID, description, total ordered, and revenue.
    """
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
    """
    Identifies trends by analyzing which menu items are frequently ordered together over a specified period.
    The function queries the database to find pairs of items that are often included in the same orders and ranks them by frequency.

    Args:
        request (HttpRequest): The HTTP request object.
        startDate (date): The start date for the report period.
        endDate (date): The end date for the report period.

    Returns:
        list[dict]: A list of dictionaries, each representing a pair of items and the frequency with which they were ordered together.
    """
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

def orderManagement(request):
    """
    Manages and updates the status of orders through an interface that allows viewing, completing, or cancelling orders.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing metadata and user actions.

    Returns:
        HttpResponse: Renders the ordermanagement.html template with order details or redirects after performing an action.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

    context = {}
    if request.method == 'POST':
        if 'submit_date' in request.POST:
            startDate = request.POST.get('startDate')
            endDate = request.POST.get('endDate')
            # validate dates
            if validateDate(request, startDate, endDate) == False:
                return redirect('Revs-ordermanagement-screen')
            orders = Orders.objects.filter(order_time__date__range=[startDate, endDate])
        elif 'submit_id' in request.POST:
            order_id = request.POST.get('orderID')
            orders = [Orders.objects.get(id=order_id)]
        elif 'complete_order' in request.POST:
            order_id = request.POST.get('complete_order')
            order = Orders.objects.get(id=order_id)
            order.status = 'Complete'
            order.save()
            return redirect('Revs-ordermanagement-screen')
        elif 'cancel_order' in request.POST:
            order_id = request.POST.get('cancel_order')
            order = Orders.objects.get(id=order_id)
            order.status = 'Cancelled'
            order.save()
            return redirect('Revs-ordermanagement-screen')
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

def getOrderItems(order_id):
    """
    Retrieves the descriptions of all menu items associated with a specific order.
    This function queries the database to get a list of item descriptions.

    Args:
        order_id (int): The specific ID of the order to retrieve item descriptions.

    Returns:
        list[str]: A list of descriptions for each menu item included in the order.
    """
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
    """
    Displays a report on the popularity of menu items based on the number of times they were ordered over a specified date range.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object.

    Returns:
        HttpResponse: Renders the popularity.html template with popularity data.
    """
    # Check if whoever is accessing the page is allowed to access it
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager == False:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')

    startingDate = timezone.now().date() - timedelta(days=365)
    endingDate = timezone.now().date()
    item_limit = 10 

    if request.method == "POST":
        startingDate = request.POST.get('startDate')
        endingDate = request.POST.get('endDate')
        item_limit = request.POST.get('item_limit', '10')

        # validate dates
        if validateDate(request, startingDate, endingDate) == False:
            return redirect('Revs-popularity-Screen')

    # Obtain the popularity data with the given dates and send context to HTML for processing
    popularityReport = getPopularityData(request, startingDate, endingDate, item_limit)
    context = {
        'report': popularityReport,
        'startDate': startingDate,
        'endDate': endingDate
    }

    return render(request, 'manager/popularity.html', context)

def getPopularityData(request, startDate, endDate, limit):
    """
    Fetches data on the popularity of menu items based on the number of times each has been ordered within a specified date range.
    The function performs a query to count orders per item, ordering the results by popularity and limiting to the desired number of results.

    Args:
        request (HttpRequest): The HTTP request object.
        startDate (date): The start date for the report period.
        endDate (date): The end date for the report period.
        limit (int): The maximum number of items to return in the report and chart.

    Returns:
        list[dict]: A list of dictionaries, each containing a menu item's ID, description, and order count.
    """
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
    """
    Sorts data in various reports dynamically based on the user's selection of sort parameters via GET request.
    Access is restricted to authenticated users with manager privileges.

    Args:
        request (HttpRequest): The HTTP request object containing sort parameters.

    Returns:
        HttpResponse: Re-renders the relevant table view with sorted data.
    """
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