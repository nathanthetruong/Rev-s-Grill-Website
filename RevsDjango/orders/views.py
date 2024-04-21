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


# Initializes all the menu items buttons
def orders(request):
    with connection.cursor() as cursor:
        if 'cart' in request.session:
            del request.session['cart']

        # Gets a list of all the menu items and sorts in alphabetical order
        cursor.execute("SELECT description, price, category, id FROM menu_items")
        data = cursor.fetchall()
        data.sort()
        buttonData = [{'description': currentItem[0], 'price': currentItem[1],
                        'category': currentItem[2], 'id': currentItem[3]} for currentItem in data]
        
        menuItems = {currentItem[3]: {'description': currentItem[0], 'price': currentItem[1],
                        'category': currentItem[2], 'count': 1} for currentItem in data}

        request.session['menuItems'] = menuItems

        # Categorize buttons based on their descriptions
        categorized_buttons = {
            'Burgers': [],
            'Baskets': [],
            'Sandwiches': [],
            'Shakes': [],
            'Beverages': [],
            'Sides': []
        }

        for button in buttonData:
            category = button['category']
            if category == 'Burger':
                categorized_buttons['Burgers'].append(button)
            elif category == 'Value Meal':
                categorized_buttons['Baskets'].append(button)
            elif category == 'Sandwiches':
                categorized_buttons['Sandwiches'].append(button)
            elif category == 'Shakes/More':
                categorized_buttons['Shakes'].append(button)
            elif category == 'Drink':
                categorized_buttons['Beverages'].append(button)
            else:
                categorized_buttons['Sides'].append(button)

        context = {'categorized_buttons': categorized_buttons}

        return render(request, 'orders/orders.html', context)


def addItem(request):
    if request.method == 'POST':
        price = float(request.POST.get('price'))
        buttonData = request.POST.get('buttonData')

        # Retrieve the cart from the session, add new price to total
        if 'cart' not in request.session:
            request.session['cart'] = {'totalPrice': 0.0, 'menuItems': []}
        cart = request.session.get('cart')
        cart['totalPrice'] += price
        totalPrice = cart['totalPrice']

        # Adds to cart is the item isn't in cart, if it is, adds to the count
        menuItems = request.session['menuItems']
        currentMenuItem = menuItems[buttonData['id']]
        if currentMenuItem in cart['menuItems']:
            cart['menuItems'][buttonData['id']]['count'] += 1
        else:
            cart['menuItems'].append(currentMenuItem)

        request.session['cart'] = cart

        return JsonResponse({'cartItems': cart['menuItems'], 'cartCount': len(cart['menuItems']),
                             'totalPrice': totalPrice})
    
    return JsonResponse({'error': 'failed'}, status=400)

# def addItem(request):
#     if request.method == 'POST':
#         price = float(request.POST.get('price'))
#         description = request.POST.get('description')

#         # Retrieve the cart from the session, add new price to total, then update cart 
#         cart = request.session.get('cart', {})
#         cart[description] = cart.get(description, 0) + price
#         request.session['cart'] = cart
#         total_price = sum(cart.values())

#         return JsonResponse({'cart_count': len(cart), 'total_price': total_price})
    
#     return JsonResponse({'error': 'failed'}, status=400)

# def checkout(request):
#     if request.method == 'POST':

#         # Defaults
#         customerId = 1
#         employeeId = 1111
#         orderTime = timezone.now()

#         cart = request.session.get('cart')
#         totalPrice = cart['total_price']

#         # Loops until the order is processed fully in the database successfully
#         while (True):
#             with transaction.atomic():
#                 try:
#                     orderId = getNewOrderID()
#                     updateOrders(customerId, employeeId, totalPrice, orderTime, orderId)
#                     for currentId in cart['ids']:
#                         ingredientIds = getUsedInventoryItems(orderId, currentId)
#                         updateInventory(ingredientIds)

#                     break

#                 # Waits for 0.1 seconds before retrying order submission
#                 except IntegrityError:
#                     time.sleep(0.1)

#         # Reset price
#         del request.session['cart']

#         messages.success(request, 'Success')
#         return redirect('Revs-Order-Screen')

def checkout(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        total_price = sum(cart.values())
        request.session['checkout_items'] = cart  
        request.session['total_price'] = total_price
        return redirect('transaction') 

def transaction_view(request):
    cart = request.session.get('cart', {'totalPrice': 0.0, 'menuItems': []})
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
                    for currentItem in cart['menuItems']:
                        for count in range(cart['menuItems']['count']):
                            ingredientIds = getUsedInventoryItems(orderId, currentItem["id"])
                            updateInventory(ingredientIds)
                    break

                # Waits for 0.1 seconds before retrying order submission
                except IntegrityError:
                    time.sleep(0.1)

        # Resets the cart
        del request.session['cart']

        messages.success(request, 'Payment/Order is successful.')
        return JsonResponse({'success': True})

    totalPriceRounded = round(totalPrice, 2)
    tax = round(0.05 * totalPrice, 2) # Calculate tax (5% of total) and round to two decimal places
    total = round(totalPrice + tax, 2)
    context = {'cartItems': cart['menuItems'], 'totalPrice': totalPriceRounded, 'tax': tax, 'total': total}
    return render(request, 'orders/transaction.html', context)


def order_return(request):
    return render(request, 'orders/orders.html')

def get_cart_items(request):
    # Retrieve cart items from the session
    cart_items = request.session.get('cart', {})
   
    # Convert the cart items dictionary to a list of dictionaries
    cart_items_list = [{'name': name, 'price': price} for name, price in cart_items.items()]
    
    # Return the cart items as JSON response
    return JsonResponse(cart_items_list, safe=False)

def login_view(request):
    # Your login logic here
    return render(request, 'login/login.html')

# Handles getting a new order ID
def getNewOrderID():
    # Get a new valid ID for the order
    with connection.cursor() as cursor:
        cursor.execute("SELECT MAX(id) FROM orders")
        orderID = cursor.fetchone()[0] + 1
    
    return orderID

# Handles updating the orders table
def updateOrders(customerId, employeeId, totalPrice, orderTime, orderId):
    # Inputs the order information into the orders table
    with connection.cursor() as cursor:
        sqlCommand = ("INSERT INTO orders (id, customer_id, employee_id, total_price, order_time) " +
                    "VALUES (%s, %s, %s, %s, %s)")
        cursor.execute(sqlCommand, [orderId, customerId, employeeId, totalPrice, orderTime])

# Gets a list of all inventory items needed to be updated
def getUsedInventoryItems(orderId, currentId):
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

# Handles updating all the items in a single menu item
def updateInventory(ingredientIds):
    # Updates all the ingredient's quantity in the inventory table
    for currentIngredientID in ingredientIds:
        with connection.cursor() as cursor:
            sqlCommand = "UPDATE inventory SET quantity_remaining = quantity_remaining - 1 WHERE id = %s"
            cursor.execute(sqlCommand, [currentIngredientID])

