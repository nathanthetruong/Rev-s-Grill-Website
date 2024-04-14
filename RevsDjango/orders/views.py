import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.utils import timezone
from django.contrib import messages

# Class to store all information on a menu item
class MenuItem:
    def __init__(self, description, price, id, category):
        self.description = description
        self.price = price
        self.id = id
        self.category = category

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
                        'category': currentItem[2]} for currentItem in data]

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
            if button['category'] == 'Burger':
                categorized_buttons['Burgers'].append(button)
            elif button['category'] == 'Value Meal':
                categorized_buttons['Baskets'].append(button)
            elif button['category'] == 'Sandwiches':
                categorized_buttons['Sandwiches'].append(button)
            elif button['category'] == 'Shakes/More':
                categorized_buttons['Shakes'].append(button)
            elif button['category'] == 'Drink':
                categorized_buttons['Beverages'].append(button)
            else:
                categorized_buttons['Sides'].append(button)

        context = {'categorized_buttons': categorized_buttons}

        return render(request, 'orders/orders.html', context)


def cart_view(request):
    return render(request, 'orders/cart.html')

def addItem(request):
    if request.method == 'POST':
        price = float(request.POST.get('price'))
        description = request.POST.get('description')

        # Use a session so we don't have concurrency issues with global variables breaking heroku
        # Retrieve the cart from the session, add new price to total, then update cart 
        cart = request.session.get('cart', {})
        cart[description] = cart.get(description, 0) + price
        request.session['cart'] = cart
        total_price = sum(cart.values())

        return JsonResponse({'cart_count': len(cart), 'total_price': total_price})
    
    return JsonResponse({'error': 'failed'}, status=400)

def checkout(request):
    if request.method == 'POST':

        # Defaults
        customerId = 1
        employeeId = 1111
        orderTime = timezone.now()

        cart = request.session.get('cart', {})
        totalPrice = sum(cart.values())
        descriptions = cart.keys()



        # Get a new valid ID for the order
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM orders")
            orderID = cursor.fetchone()[0] + 1

        # Insert into orders table
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO orders (id, customer_id, employee_id, total_price, order_time) VALUES (%s, %s, %s, %s, %s)", [orderID, customerId, employeeId, totalPrice, orderTime])

        # Reset price
        del request.session['cart']

        messages.success(request, 'Success')
        return redirect('Revs-Order-Screen') 