from django.urls import path
from . import views

'''
This is the menu page routing logic.
'''

urlpatterns = [
    path('', views.menu, name='Revs-Menu-Screen'),
]