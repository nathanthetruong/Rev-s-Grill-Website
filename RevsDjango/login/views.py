import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection
from allauth.socialaccount.views import SignupView
from allauth.socialaccount.models import SocialLogin
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import perform_login
from .models import Employees


"""
    Renders the login page.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered login page.
"""
def login(request):
    return render(request, 'login/login.html')

"""
    Renders the about page.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered about page.
"""
def about(request):
    return render(request, 'login/about.html')

"""
    Renders the help page.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered help page.
"""
def help(request):
    return render(request, 'login/help.html')


"""
    Renders the employee page if the user is authenticated and an employee.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered employee page if authenticated and employee, otherwise redirects to 'employee-noaccess' page.
"""
def employee(request):

    # First check if an employee is accessing the page
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    if Employees.objects.filter(email=user_email).exists() == False:
        return redirect('employee-noaccess')

    return render(request, 'login/employee.html')

"""
    Renders the 'noaccess' page.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered 'noaccess' page.
"""
def noaccess(request):
    return render(request, 'login/noaccess.html')

"""
    Renders the 'noaccessmanager' page.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered 'noaccessmanager' page.
"""
def noaccessManager(request):
    return render(request, 'login/noaccessmanager.html')

"""
    Renders the 'noaccessadministrator' page.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponse: Rendered 'noaccessadministrator' page.
"""
def noaccessAdmin(request):
    return render(request, 'login/noaccessadministrator.html')

"""
    Custom Signup view for handling social signups.
"""
class CustomSignupView(SignupView):
    def form_valid(self, form):
        sociallogin = self.get_form_kwargs().get('sociallogin')
        user = sociallogin.user
        if form.is_valid():
            sociallogin.save(self.request)
            return perform_login(self.request, user, email_verification='optional')
        return super().form_valid(form)

"""
    Redirects the user to the appropriate employee page based on authentication and role.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponseRedirect: Redirects to the appropriate employee page.
"""   
def employeeRedirect(request):
    if not request.user.is_authenticated:
        return redirect('Revs-Login-Screen')
    
    # Check if the user's email is in the Employee table
    user_email = request.user.email
    if Employees.objects.filter(email=user_email).exists():
        return redirect('Revs-Employee-Screen')
    else:
        return redirect('employee-noaccess')

"""
    Redirects the user to the manager page if authenticated and a manager.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponseRedirect: Redirects to the manager page if authenticated and a manager, otherwise redirects to 'manager-noaccess' page.
"""
def managerAccess(request):
    if not request.user.is_authenticated:
        return redirect('Revs-Login-Screen')
    
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_manager:
            return redirect('Revs-Manager-Screen')
        else:
            return redirect('manager-noaccess')
    except Employees.DoesNotExist:
        return redirect('manager-noaccess')

"""
    Redirects the user to the admin page if authenticated and an admin.
    Args:
        request: Django HttpRequest object.
    Returns:
        HttpResponseRedirect: Redirects to the admin page if authenticated and an admin, otherwise redirects to 'admin-noaccess' page.
"""   
def adminAccess(request):
    if not request.user.is_authenticated:
        return redirect('Revs-Login-Screen')
    
    user_email = request.user.email
    try:
        employee = Employees.objects.get(email=user_email)
        if employee.is_admin:
            return redirect('Revs-Administrator-Screen')
        else:
            return redirect('admin-noaccess')
    except Employees.DoesNotExist:
        return redirect('admin-noaccess')
