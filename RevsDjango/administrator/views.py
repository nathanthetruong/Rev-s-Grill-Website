from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import MenuItems, Inventory, Employees, Orders, Inventory
from django.db import connection
from django.utils import timezone
from datetime import datetime, timedelta
import calendar
from django import forms
from django.contrib import messages


def administrator(request):

    employees = Employees.objects.all()
    context = {
        'employees': employees,
    }

    return render(request, 'administrator/administrator.html', context)

'''
This function will give us the ability to modify the staff's properties
'''
def modifyStaff(request):
    if request.method == 'POST':
        employee_id = request.POST.get('id')
        name = request.POST.get('name')
        is_manager = request.POST.getlist('manager[]')
        email = request.POST.get('email')
        is_admin = request.POST.getlist('admin[]')

        employee = Employees.objects.get(id=employee_id)
        employee.id = employee_id
        employee.name = name
        employee.email = email
        employee.is_manager = 'on' in is_manager
        employee.is_admin = 'on' in is_admin
        employee.save()
    return redirect('Revs-Administrator-Screen')

'''
This function will give us the ability to delete staff
'''
def deleteStaff(request):
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            # Set employee_id to 0 in all related orders before deleting the employee, so the reports aren't affected
            Orders.objects.filter(employee_id=employee_id).update(employee_id=0)
            # Delete the employee
            Employees.objects.filter(id=employee_id).delete()

        return redirect('Revs-Administrator-Screen')

'''
This function will give us the ability to add new staff
'''
def addStaff(request):
    if request.method == 'POST':
        employee_id = request.POST.get('new_id')
        name = request.POST.get('new_name')
        is_manager = request.POST.getlist('new_manager[]')
        is_admin = request.POST.getlist('new_admin[]')

        # Check if the employee ID already exists
        if Employees.objects.filter(id=employee_id).exists():
            messages.error(request, 'Employee ID already in use. Please use a different ID.')
            return redirect('Revs-staffmanagement-screen')
        else:
            # Create new employee since ID is unique
            new_employee = Employees(id=employee_id, name=name, is_manager='on' in is_manager, is_admin='on' in is_admin)
            new_employee.save()
            messages.success(request, 'New employee added successfully.')
            return redirect('Revs-Administrator-Screen')
        