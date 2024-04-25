from django.urls import path
from . import views

'''
This is the login page routing logic.
'''

urlpatterns = [
    path('', views.administrator, name='Revs-Administrator-Screen'),
]
