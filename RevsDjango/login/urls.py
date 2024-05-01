from django.urls import path
from . import views
from login.views import CustomSignupView

'''
This is the login page routing logic.
'''

urlpatterns = [
    path('', views.login, name='Revs-Login-Screen'),
    path('about/', views.about, name='Revs-About-Screen'),
    path('employee/', views.employee, name='Revs-Employee-Screen'),
    path('social/signup/', CustomSignupView.as_view(), name='socialaccount_signup'),
    path('employeeredirect/', views.employeeRedirect, name='employee-redirect'),
    path('noaccess/', views.noaccess, name='employee-noaccess'),
    path('manageraccess/', views.managerAccess, name='manager-access'),
    path('noaccessmanager/', views.noaccessManager, name='manager-noaccess'),
    path('adminaccess/', views.adminAccess, name='admin-access'),
    path('noaccessadmin/', views.noaccessAdmin, name='admin-noaccess'),
    path('help/', views.help, name='Revs-Help-Screen'),
]
