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

        return render(request, 'orders/orders.html', context)


def addItem(request):
    if request.method == 'POST':
        price = float(request.POST.get('price'))
        id = request.POST.get('id')

        # Retrieve the cart from the session, add new price to total, then update cart 
        if 'cart' not in request.session:
            request.session['cart'] = {'total_price': 0.0, 'ids': []}
        cart = request.session.get('cart')
        cart['total_price'] += price
        totalPrice = cart['total_price']
        cart['ids'].append(id)
        request.session['cart'] = cart

        return JsonResponse({'cart_count': len(cart['ids']), 'total_price': totalPrice})
    
    return JsonResponse({'error': 'failed'}, status=400)

# def checkout(request):
#     if request.method == 'POST':

#         # Defaults
#         customer_id = 1
#         employee_id = 1111
#         order_time = timezone.now()

#         cart = request.session.get('cart', {})
#         total_price = sum(cart.values())

#         # Get a new valid ID for the order
#         with connection.cursor() as cursor:
#             cursor.execute("SELECT MAX(id) FROM orders")
#             orderID = cursor.fetchone()[0] + 1

#         # Insert into orders table
#         with connection.cursor() as cursor:
#             cursor.execute("INSERT INTO orders (id, customer_id, employee_id, total_price, order_time) VALUES (%s, %s, %s, %s, %s)", [orderID, customer_id, employee_id, total_price, order_time])

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