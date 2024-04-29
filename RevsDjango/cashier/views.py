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
                        'category': currentItem[2]} for currentItem in data}

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

        return render(request, 'cashier/cashier.html', context)


# def addItem(request):
#     if request.method == 'POST':
#         price = float(request.POST.get('price'))
#         id = request.POST.get('id')

#         # Retrieve the cart from the session, add new price to total, then update cart 
#         if 'cart' not in request.session:
#             request.session['cart'] = {'total_price': 0.0, 'ids': []}
#         cart = request.session.get('cart')
#         cart['total_price'] += price
#         totalPrice = cart['total_price']
#         cart['ids'].append(id)
#         request.session['cart'] = cart

#         return JsonResponse({'cart_count': len(cart['ids']), 'total_price': totalPrice})
    
#     return JsonResponse({'error': 'failed'}, status=400)
def addItem(request):
    if request.method == 'POST':
        price = float(request.POST.get('price'))
        description = request.POST.get('description')
        quantity = request.POST.get('quantity')

        # Retrieve the cart from the session, add new price to total, then update cart 
        cart = request.session.get('cart', {})
        for i in range(quantity):
            cart[description] = cart.get(description, 0) + price
            request.session['cart'] = cart
            total_price = sum(cart.values())

        return JsonResponse({'cart_count': len(cart), 'total_price': total_price})
    
    return JsonResponse({'error': 'failed'}, status=400)

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
    if request.method == 'POST':
        # Retrieve form data
        total_price = request.POST.get('total_price')
       
        # Insert into orders table
        customer_id = 1
        employee_id = 1111
        order_time = timezone.now()
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM orders")
            orderID = cursor.fetchone()[0] + 1
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO orders (id, customer_id, employee_id, total_price, order_time) VALUES (%s, %s, %s, %s, %s)", [orderID, customer_id, employee_id, total_price, order_time])
        
        # Reset price and clear session cart
        del request.session['checkout_items']
        del request.session['total_price']
        messages.success(request, 'Payment/Order is successful.')
        return JsonResponse({'success': True})

    cart_items = request.session.get('checkout_items', {})
    total_price = sum(cart_items.values())  # Calculate total price of all items
    tax = round(0.05 * total_price, 2)  # Calculate tax (5% of total) and round to two decimal places
    total = round(total_price + tax, 2)  
    total_price_rounded = round(total_price, 2)  
    context = {'cart_items': cart_items, 'total_price': total_price_rounded, 'tax': tax, 'total': total}
    return render(request, 'cashier/transaction.html', context)


def order_return(request):
    return render(request, 'cashier/cashier.html')

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
        cursor.execute("SELECT MAX(id) FROM cashier")
        orderID = cursor.fetchone()[0] + 1
    
    return orderID

# Handles updating the cashier table
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

##Kitchen functions
def orderStatus(request):
    with connection.cursor() as cursor:
        sqlCommand = "SELECT * FROM orders WHERE status IN ('in_progress', 'cancelled')"
        cursor.execute(sqlCommand)
        cursorOutput = cursor.fetchall()
        dataSorted = sorted(cursorOutput, key=lambda x: x[0])
        dataReport =[{'id': currentItem[0], 'total_price': currentItem[3],
                       'order_time': currentItem[4], 'status': currentItem[5]}
                       for currentItem in dataSorted]
    return render(request, 'cashier/kitchen.html', dataReport)

def cancelOrder(request, orderId):
    if request.method == 'POST':
        orderId = request.POST.get('id')
    with connection.cursor() as cursor:
        cursor.execute("UPDATE orders SET status = %s WHERE id = %s", ['cancelled', orderId])
    return JsonResponse({'success': True})


def CompleteOrder(request):
    if request.method == 'POST':
        orderId = request.POST.get('id')
    with connection.cursor() as cursor:
        cursor.execute("UPDATE orders SET status = %s WHERE id = %s", ['completed', orderId])
    return JsonResponse({'success': True})

def orderManagement(request):
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