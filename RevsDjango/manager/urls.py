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
]