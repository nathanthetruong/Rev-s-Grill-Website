import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection

# # Create your views here.
# def orders(request):
#     return render(request, 'orders/orders.html')

# Initializes all the menu items buttons
def orders(request):
    with connection.cursor() as cursor:
        # Gets a list of all the menu items and sorts in alphabetical order
        cursor.execute("SELECT description FROM menu_items")
        data = cursor.fetchall()
        data.sort()
        buttonData = [{'description': currentItem[0]} for currentItem in data]

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
