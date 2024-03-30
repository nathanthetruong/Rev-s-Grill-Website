import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection

# Create your views here.
def test_SQL(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM menu_items")
        data = cursor.fetchall()
        print(data)
    return JsonResponse({'result': data})

# Returns 1 if employee is a manager
# Returns 0 if the employee isn't a manager
# Returns -1 if the ID doesn't belong to an employee
def authenticateUser(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        employeeId = data.get('user_input', '')
        if not employeeId:
            return JsonResponse({'error': "Empty Field"})
        with connection.cursor() as cursor:
            cursor.execute("SELECT is_manager FROM employees WHERE id=%s", [int(employeeId)])
            data = cursor.fetchall()

            if len(data) > 0:
                if data[0][0]:
                    return JsonResponse({'result': [1]})
                else:
                    return JsonResponse({'result': [0]})
            else:
                return JsonResponse({'result': [-1]})

def login(request):
    return render(request, 'login/login.html')

def about(request):
    return render(request, 'login/about.html')