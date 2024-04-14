from django.urls import path
from . import views

'''
This is the login page routing logic.
'''

urlpatterns = [
    path('', views.login, name='Revs-Login-Screen'),
    path('authenticate-user/', views.authenticateUser, name='authenticate-user'),
    path('about/', views.about, name='Revs-About-Screen'),
    path('employee/', views.employee, name='Revs-Employee-Screen'),
]
