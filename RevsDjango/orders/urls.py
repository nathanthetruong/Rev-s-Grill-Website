from django.urls import path
from . import views

'''
This is the order page routing logic.
'''

urlpatterns = [
    path('', views.orders, name='Revs-Order-Screen'),
]