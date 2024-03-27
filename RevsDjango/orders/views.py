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

        context = {'buttonData': buttonData}
        return render(request, 'orders/orders.html', context)
