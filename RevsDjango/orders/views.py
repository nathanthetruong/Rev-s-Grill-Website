import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection
from django.utils import timezone
from django.contrib import messages

# # Create your views here.
# def orders(request):
#     return render(request, 'orders/orders.html')

currentPrice = 0.0

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
        # Gets a list of all the menu items and sorts in alphabetical order
        cursor.execute("SELECT description, price FROM menu_items")
        data = cursor.fetchall()
        data.sort()
        buttonData = [{'description': currentItem[0], 'price': currentItem[1]} for currentItem in data]

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
            if 'Burger' in button['description']:
                categorized_buttons['Burgers'].append(button)
            elif 'Tender' in button['description'] or 'Meal' in button['description']:
                categorized_buttons['Baskets'].append(button)
            elif 'Sandwich' in button['description'] or 'Wrap' in button['description'] or 'Patty' in button['description']:
                categorized_buttons['Sandwiches'].append(button)
            elif 'Shake' in button['description'] or 'Ice' in button['description']:
                categorized_buttons['Shakes'].append(button)
            elif 'Drink' in button['description'] or'Water' in button['description'] or 'Beer' in button['description']:
                categorized_buttons['Beverages'].append(button)
            else:
                categorized_buttons['Sides'].append(button)

        context = {'categorized_buttons': categorized_buttons}

        # context = {'buttonData': buttonData}
        return render(request, 'orders/orders.html', context)


def cart_view(request):
    return render(request, 'orders/cart.html')

def addItem(request):
    global currentPrice

    if request.method == 'POST':
        price = float(request.POST.get('price'))
        currentPrice += price

        return JsonResponse({'cart_count': 1, 'total_price': currentPrice})
    
    return JsonResponse({'error': 'failed'}, status=400)

def checkout(request):
    if request.method == 'POST':

        # Defaults
        global currentPrice
        customer_id = 1
        employee_id = 1111
        total_price = currentPrice
        order_time = timezone.now()

        # Get a new valid ID for the order
        with connection.cursor() as cursor:
            cursor.execute("SELECT MAX(id) FROM orders")
            orderID = cursor.fetchone()[0] + 1

        # Insert into orders table
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO orders (id, customer_id, employee_id, total_price, order_time) VALUES (%s, %s, %s, %s, %s)", [orderID, customer_id, employee_id, total_price, order_time])

        # Reset price
        currentPrice = 0.0

        messages.success(request, 'Success')
        return redirect('Revs-Order-Screen') 