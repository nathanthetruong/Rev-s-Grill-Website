from django.urls import path
from . import views

'''
This is the login page routing logic.
'''

urlpatterns = [
    path('', views.login, name='Revs-Login-Screen'),
    path('about/', views.about, name='Revs-About-Screen'),
]
