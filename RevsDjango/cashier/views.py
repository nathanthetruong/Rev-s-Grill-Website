import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection, transaction, IntegrityError
from django.utils import timezone
from django.contrib import messages
from .models import CartItem
from collections import defaultdict
import time
from .models import MenuItems, Inventory, Employees, Orders, Inventory, OrderBreakout

def help(request):
    """
        Renders the help page.
        Args:
            request: Django HttpRequest object.
        Returns:
            HttpResponse: Rendered help page.
    """
    return render(request, 'login/help.html')

def orders(request):
    """
        Renders the cashier page if the user is authenticated and an employee.
        Args:
            request: Django HttpRequest object.
        Returns:
            HttpResponse: Rendered cashier page if authenticated and employee, otherwise redirects to 'employee-noaccess' page.
    """
    # First check if an employee is accessing the page
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    if Employees.objects.filter(email=user_email).exists() == False:
        return redirect('employee-noaccess')
        

    with connection.cursor() as cursor:
        if 'cart' in request.session:
            del request.session['cart']

        # Gets a list of all the menu items and sorts in alphabetical order
        cursor.execute("SELECT description, price, category, id FROM menu_items")
        data = cursor.fetchall()
        data.sort()
        menuItems = [{'description': currentItem[0], 'price': currentItem[1],
                        'category': currentItem[2], 'id': currentItem[3],
                        'count': 1} for currentItem in data]

        request.session['menuItems'] = menuItems

        # Categorize buttons based on their descriptions
        categorizedButtons = {
            'Burgers': [],
            'Baskets': [],
            'Sandwiches': [],
            'Shakes': [],
            'Beverages': [],
            'Sides': []
        }

        for button in menuItems:
            category = button['category']
            if category == 'Burger':
                categorizedButtons['Burgers'].append(button)
            elif category == 'Value Meal':
                categorizedButtons['Baskets'].append(button)
            elif category == 'Sandwiches':
                categorizedButtons['Sandwiches'].append(button)
            elif category == 'Shakes/More':
                categorizedButtons['Shakes'].append(button)
            elif category == 'Drink':
                categorizedButtons['Beverages'].append(button)
            else:
                categorizedButtons['Sides'].append(button)

        context = {'categorizedButtons': categorizedButtons}

        return render(request, 'cashier/cashier.html', context)

def addItem(request):
    """
        Adds items to the cart.
        Args:
            request: Django HttpRequest object.
        Returns:
            JsonResponse: JSON response containing updated cart items, cart count, and total price.
    """
    if request.method == 'POST':
        price = float(request.POST.get('price'))
        buttonId = request.POST.get('id')

        # Retrieve the cart from the session, add new price to total
        if 'cart' not in request.session:
            request.session['cart'] = {'totalPrice': 0.0, 'menuItems': []}
        cart = request.session.get('cart')
        cart['totalPrice'] += price
        totalPrice = cart['totalPrice']

        # Adds to cart is the item isn't in cart, if it is, adds to the count
        for menuItem in cart['menuItems']:
            if menuItem['id'] == int(buttonId):
                menuItem['count'] += 1
                break
        else:
            cart['menuItems'].append(getMenuItem(request, buttonId))

        request.session['cart'] = cart
        cartCount = 0
        for menuItem in cart['menuItems']:
            cartCount += menuItem['count']

        return JsonResponse({'cartItems': cart['menuItems'], 'cartCount': cartCount,
                             'totalPrice': totalPrice})
    
    return JsonResponse({'error': 'failed'}, status=400)

def removeItem(request):
    """
        Removes items from the cart.
        Args:
            request: Django HttpRequest object.
        Returns:
            JsonResponse: JSON response containing updated cart items, cart count, and total price.
    """
    if request.method == 'POST':
        price = float(request.POST.get('price'))
        buttonId = request.POST.get('id')
        # Retrieve the cart from the session, add new price to total
        cart = request.session.get('cart')
        cart['totalPrice'] -= price
        totalPrice = cart['totalPrice']
        # Adds to cart is the item isn't in cart, if it is, adds to the count
        for menuItem in cart['menuItems'][:]:
            if menuItem['id'] == int(buttonId):
                menuItem['count'] -= 1
                if menuItem['count'] < 1:
                    cart['menuItems'].remove(menuItem)
                break
        request.session['cart'] = cart
        cartCount = len(cart['menuItems'])
        return JsonResponse({'cartItems': cart['menuItems'], 'cartCount': cartCount,
                             'totalPrice': totalPrice})
    
    return JsonResponse({'error': 'failed'}, status=400)

def removeAllIems(request):
    """
        Removes all occurrences of a specific item from the cart.
        Args:
            request: Django HttpRequest object.
        Returns:
            JsonResponse: JSON response containing updated cart items, cart count, and total price.
    """
    if request.method == 'POST':
        price = float(request.POST.get('price'))
        buttonId = request.POST.get('id')

        # Removes item from cart
        cart = request.session.get('cart')
        for menuItem in cart['menuItems'][:]:
            if menuItem['id'] == int(buttonId):
                count = menuItem['count']
                cart['totalPrice'] -= count * price
                cart['menuItems'].remove(menuItem)
                break
        
        request.session['cart'] = cart
        totalPrice = cart['totalPrice']

        cartCount = len(cart['menuItems'])

        return JsonResponse({'cartItems': cart['menuItems'], 'cartCount': cartCount,
                             'totalPrice': totalPrice})
    
    return JsonResponse({'error': 'failed'}, status=400)

def checkout(request):
    """
        Redirects to the transaction view.
        Args:
            request: Django HttpRequest object.
        Returns:
            HttpResponseRedirect: Redirects to the transaction view.
    """
    if request.method == 'POST':
        return redirect('cashierTransaction') 
      
def transactionView(request):
    """
        Handles the transaction process.
        Args:
            request: Django HttpRequest object.
        Returns:
            HttpResponse: Rendered transaction page.
    """
    cart = request.session.get('cart', {'totalPrice': 0.0, 'menuItems': {}})
    totalPrice = cart['totalPrice']

    if request.method == 'POST':
        # Defaults
        customerId = 1
        employeeId = 1111
        orderTime = timezone.now()

        # Loops until the order is processed fully in the database successfully
        while (True):
            with transaction.atomic():
                try:
                    orderId = getNewOrderID()
                    updateOrders(customerId, employeeId, totalPrice, orderTime, orderId)
                    for menuItem in cart['menuItems']:
                        for count in range(menuItem['count']):
                            ingredientIds = getUsedInventoryItems(orderId, menuItem["id"])
                            updateInventory(ingredientIds)
                    break

                # Waits for 0.1 seconds before retrying order submission
                except IntegrityError:
                    time.sleep(0.1)

        # Resets the cart
        del request.session['cart']

        messages.success(request, 'Payment/Order is successful.')
        return JsonResponse({'success': True})

    # Handles tax and total calculation
    totalPriceRounded = round(totalPrice, 2)
    tax = round(0.05 * totalPrice, 2)
    total = round(totalPrice + tax, 2)

    context = {'cartItems': cart['menuItems'], 'totalPrice': totalPriceRounded, 'tax': tax, 'total': total}

    return render(request, 'cashier/transaction.html', context)

def order_return(request):
    """
        Renders the orders page.
        Args:
            request: Django HttpRequest object.
        Returns:
            HttpResponse: Rendered orders page.
    """
    return render(request, 'cashier/cashier.html')

def getCartItems(request):
    """
        Retrieves cart items from the session.
        Args:
            request: Django HttpRequest object.
        Returns:
            JsonResponse: JSON response containing cart items.
    """
    # Retrieve cart items from the session
    cartItems = request.session.get('cart', {'totalPrice': 0.0, 'menuItems': {}})
    context = {'cartItems': cartItems['menuItems']}
    
    # Return the cart items as JSON response
    return JsonResponse(context, safe=False)

def loginView(request):
    """
        Renders the login page.
        Args:
            request: Django HttpRequest object.
        Returns:
            HttpResponse: Rendered login page.
    """
    return render(request, 'login/login.html')

def getNewOrderID():
    """
        Gets a new order ID.
        Returns:
            int: New order ID.
    """
    # Get a new valid ID for the order
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(id) FROM orders")
        orderID = cursor.fetchone()[0] + 1
    
    return orderID

def updateOrders(customerId, employeeId, totalPrice, orderTime, orderId):
    """
        Updates the orders table.
        Args:
            customerId (int): ID of the customer.
            employeeId (int): ID of the employee.
            totalPrice (float): Total price of the order.
            orderTime (datetime): Time of the order.
            orderId (int): ID of the order.
    """
    # Inputs the order information into the orders table
    with connection.cursor() as cursor:
        sqlCommand = ("INSERT INTO orders (id, customer_id, employee_id, total_price, order_time, status) " +
                    "VALUES (%s, %s, %s, %s, %s, %s)")
        cursor.execute(sqlCommand, [orderId, customerId, employeeId, totalPrice, orderTime, "In Progress"])

def getUsedInventoryItems(orderId, currentId):
    """
        Gets a list of all inventory items needed to be updated.
        Args:
            orderId (int): ID of the order.
            currentId (int): ID of the current item.
        Returns:
            list: List of ingredient IDs.
    """
    # Handles insertion into Order Breakout
    with connection.cursor() as cursor:
        sqlCommand = "INSERT INTO order_breakout (order_id, food_items) VALUES (%s, %s)"
        cursor.execute(sqlCommand, [orderId, currentId])

    # Handles incrementing times_ordered for the menu item
    with connection.cursor() as cursor:
        sqlCommand = "UPDATE menu_items SET times_ordered = times_ordered + 1 WHERE id = %s"
        cursor.execute(sqlCommand, [currentId])

    # Finds all the ingredients to be updated in the inventory table
    with connection.cursor() as cursor:
        sqlCommand = "SELECT inventory_id FROM food_to_inventory WHERE food_item_id = %s"
        cursor.execute(sqlCommand, [currentId])
        ingredientIds = cursor.fetchall()

    return ingredientIds

def updateInventory(ingredientIds):
    """
        Updates the inventory for all ingredients.
        Args:
            ingredientIds (list): List of ingredient IDs.
    """
    # Updates all the ingredient's quantity in the inventory table
    for currentIngredientID in ingredientIds:
        with connection.cursor() as cursor:
            sqlCommand = "UPDATE inventory SET quantity_remaining = quantity_remaining - 1 WHERE id = %s"
            cursor.execute(sqlCommand, [currentIngredientID])

def getMenuItem(request, menuItemId):
    """
        Gets a specific menu item.
        Args:
            request: Django HttpRequest object.
            menuItemId (str): ID of the menu item.
        Returns:
            dict: Dictionary containing menu item information.
    """
    menuItems = request.session.get("menuItems")
    for menuItem in menuItems:
        if menuItem['id'] == int(menuItemId):
            return menuItem

def orderManagement(request):
    '''
    Function to get the required data in order management
    Args:
        request: HttpRequest object containing metadata and user data submitted through the web form.
    Returns:
        Renders the 'cashier/ordermanagement.html' template with the context containing orders and their associated menu items.
    '''
    context = {}
    if request.method == 'POST':
        if 'submit_date' in request.POST:
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
            orders = Orders.objects.filter(order_time__date__range=[start_date, end_date])
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

    return render(request, 'cashier/ordermanagement.html', context)

def getOrderItems(order_id):
    '''
    This function will get all the menu items associated with a specific order id
    Args:
        request: The ID of the order whose menu items are to be fetched
    Returns:
        list: A list of descriptions of menu items associated with the order.
    '''
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