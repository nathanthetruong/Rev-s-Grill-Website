from django.urls import path
from . import views

'''
This is the order page routing logic.
'''

urlpatterns = [
    path('', views.orders, name='Revs-Cashier-Screen'),
    path('checkout/', views.checkout, name='cashierCheckout'),
    path('add/', views.addItem, name='cashierAddItem'),
    path('transaction/', views.transactionView, name='cashierTransaction'),
    path('orders/', views.transactionView, name='cashierOrders'),
    path('getCartItems/', views.getCartItems, name='cashierGetCartItems'),
    path('login/', views.loginView, name='cashierLogin'),
    path('ordermanagement/', views.orderManagement, name='Revs-ordermanagement'),
    path('removeItem/', views.removeItem, name='cashierRemoveItem'),
    path('removeAllIems/', views.removeAllIems, name='cashierRemoveAllItems'),
    path('help/', views.help, name='Revs-Help-Screen'),
]
