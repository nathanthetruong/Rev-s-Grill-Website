from django.urls import path
from . import views

'''
This is the manager page routing logic.
'''

urlpatterns = [
    path('', views.manager, name='Revs-Manager-Screen'),
]