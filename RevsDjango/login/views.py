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

def login(request):
    return render(request, 'login/login.html')

def about(request):
    return render(request, 'login/about.html')

def employee(request):

    # First check if an employee is accessing the page
    if not request.user.is_authenticated:
        return redirect('employee-noaccess')
    user_email = request.user.email
    if Employees.objects.filter(email=user_email).exists() == False:
        return redirect('employee-noaccess')

    return render(request, 'login/employee.html')

def noaccess(request):
    return render(request, 'login/noaccess.html')

def noaccessManager(request):
    return render(request, 'login/noaccessmanager.html')

def noaccessAdmin(request):
    return render(request, 'login/noaccessadministrator.html')

class CustomSignupView(SignupView):
    def form_valid(self, form):
        sociallogin = self.get_form_kwargs().get('sociallogin')
        user = sociallogin.user
        if form.is_valid():
            sociallogin.save(self.request)
            return perform_login(self.request, user, email_verification='optional')
        return super().form_valid(form)
    
def employeeRedirect(request):
    if not request.user.is_authenticated:
        return redirect('Revs-Login-Screen')
    
    # Check if the user's email is in the Employee table
    user_email = request.user.email
    if Employees.objects.filter(email=user_email).exists():
        return redirect('Revs-Employee-Screen')
    else:
        return redirect('employee-noaccess')

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
