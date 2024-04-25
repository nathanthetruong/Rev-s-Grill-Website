from django.urls import path
from . import views

'''
This is the login page routing logic.
'''

urlpatterns = [
    path('', views.administrator, name='Revs-Administrator-Screen'),
    path('deletestaff/', views.deleteStaff, name='Revs-delete-staff'),
    path('modifystaff/', views.modifyStaff, name='Revs-modify-staff'),
    path('addstaff/', views.addStaff, name='Revs-add-staff'),
]
