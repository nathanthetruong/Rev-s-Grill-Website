import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection, transaction, IntegrityError
from django.utils import timezone
from django.contrib import messages
from collections import defaultdict
import time


"""
    Renders the menu board page with categorized menu items.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered menu board page.
"""
def menu_board(request):
    with connection.cursor() as cursor:
        if 'cart' in request.session:
            del request.session['cart']

        cursor.execute("SELECT description, price, category, id FROM menu_items")
        data = cursor.fetchall()
        data.sort()
        menuItems = [{'description': currentItem[0], 'price': currentItem[1],
                        'category': currentItem[2], 'id': currentItem[3],
                        'count': 1} for currentItem in data]

        request.session['menuItems'] = menuItems

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

        return render(request, 'menuboard/menuboard.html', context)


"""
    Renders the help page.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered help page.
"""
def help(request):
    return render(request, 'login/help.html')