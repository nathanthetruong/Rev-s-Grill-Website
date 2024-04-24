from django.urls import path
from . import views

'''
This is the manager page routing logic.
'''

urlpatterns = [
    path('', views.manager, name='Revs-Manager-Screen'),
    path('excess/', views.excess, name='Revs-excess-Screen'),
    path('productusage/', views.productusage, name='Revs-productusage-Screen'),
    path('restock/', views.restock, name='Revs-restock-Screen'),
    path('sales/', views.sales, name='Revs-sales-Screen'),
    path('trends/', views.trends, name='Revs-trends-Screen'),
    path('ordermanagement/', views.orderManagement, name='Revs-ordermanagement-screen'),
    path('staffmanagement/', views.displayStaff, name='Revs-staffmanagement-screen'),
    path('deletemenuitem/', views.deleteItem, name='Revs-delete-item'),
    path('modifymenuitem/', views.modifyItem, name='Revs-modify-item'),
    path('deletestaff/', views.deleteStaff, name='Revs-delete-staff'),
    path('modifystaff/', views.modifyStaff, name='Revs-modify-staff'),
    path('addstaff/', views.addStaff, name='Revs-add-staff'),
    path('addinventory/', views.addInventory, name='Revs-add-inventory'),
    path('deleteinventory/', views.deleteInventory, name='Revs-delete-inventory'),
    path('modifyinventory/', views.modifyInventory, name='Revs-modify-inventory'),
]