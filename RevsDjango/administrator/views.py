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
    """
    Displays the administrator page with a list of all employees.
    Access is restricted to authenticated users with admin privileges.

    Args:
        request (HttpRequest): The HTTP request object containing user session data.

    Returns:
        HttpResponse: Renders the administrator page with employee data or redirects to no access pages.
    """
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_admin:
            employees = Employees.objects.all()
            context = {
                'employees': employees,
            }
            return render(request, 'administrator/administrator.html', context)

        else:
            return redirect('admin-noaccess')
    except Employees.DoesNotExist:
        return redirect('employee-noaccess')
    
def modifyStaff(request):
    """
    Modifies the properties of an existing staff member based on form data received via a POST request.
    This function updates details such as name, manager status, admin status, and email in the PSQL database.

    Args:
        request (HttpRequest): The HTTP request object containing the updated staff details.

    Returns:
        HttpResponse: Redirects to the administrator management screen after updating the employee data.
    """
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

def deleteStaff(request):
    """
    Deletes a staff member from the database using the employee ID provided through a POST request.
    Also, this sets the employee_id in related orders to 0 so the reports aren't affected.

    Args:
        request (HttpRequest): The HTTP request object containing the employee ID to delete.

    Returns:
        HttpResponse: Redirects to the administrator screen with a success message after deleting the employee.
    """
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        if employee_id:
            # Set employee_id to 0 in all related orders before deleting the employee, so the reports aren't affected
            Orders.objects.filter(employee_id=employee_id).update(employee_id=0)
            # Delete the employee
            Employees.objects.filter(id=employee_id).delete()
            messages.success(request, 'Deleted employee successfully.')

        return redirect('Revs-Administrator-Screen')

def addStaff(request):
    """
    Adds a new staff member to the database using data from a POST request.
    Validates that the employee ID and email are unique before creation. If either is already in use, it returns an error message.
    Upon successful creation, the new staff member is saved in the database.

    Args:
        request (HttpRequest): The HTTP request object containing new staff member details.

    Returns:
        HttpResponse: Redirects to the administrator screen with either a success or error message.
    """
    if request.method == 'POST':
        employee_id = request.POST.get('new_id')
        name = request.POST.get('new_name')
        is_manager = request.POST.getlist('new_manager[]')
        is_admin = request.POST.getlist('new_admin[]')
        email = request.POST.get('new_email')

        # Check if the employee ID or email already exists
        if Employees.objects.filter(id=employee_id).exists():
            messages.error(request, 'Employee ID already in use. Please use a different ID.')
            return redirect('Revs-staffmanagement-screen')
        elif Employees.objects.filter(email=email).exists():
            messages.error(request, 'Email already in use. Please use a different email.')
            return redirect('Revs-Administrator-Screen')
        else:
            # Create new employee since ID is unique
            new_employee = Employees(id=employee_id, name=name, email=email, is_manager='on' in is_manager, is_admin='on' in is_admin)
            new_employee.save()
            messages.success(request, 'New employee added successfully.')
            return redirect('Revs-Administrator-Screen')
        