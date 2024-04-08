from django.urls import path
from . import views

'''
This is the order page routing logic.
'''

urlpatterns = [
    path('', views.orders, name='Revs-Order-Screen'),
    path('checkout/', views.checkout, name='checkout'),
    path('add/', views.addItem, name='addItem'),
    path('transaction/', views.transaction_view, name='transaction'),
    path('orders/', views.transaction_view, name='orders'),
    path('get_cart_items/', views.get_cart_items, name='get_cart_items'),
    path('login/', views.login_view, name='login'),
    
]