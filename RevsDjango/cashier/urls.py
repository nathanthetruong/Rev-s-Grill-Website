from django.urls import path
from . import views

'''
This is the order page routing logic.
'''

urlpatterns = [
    path('', views.orders, name='Revs-Cashier-Screen'),
    path('checkout/', views.checkout, name='cashierCheckout'),
    path('add/', views.addItem, name='cashierAddItem'),
    path('transaction/', views.transaction_view, name='cashierTransaction'),
    path('orders/', views.transaction_view, name='cashierOrders'),
    path('getCartItems/', views.get_cart_items, name='cashierGetCartItems'),
    path('login/', views.login_view, name='cashierLogin'),
    path('ordermanagement/', views.orderManagement, name='Revs-ordermanagement'),
    path('removeItem/', views.removeItem, name='cashierRemoveItem'),
    path('removeAllIems/', views.removeAllIems, name='cashierRemoveAllItems'),
    path('textToSpeech/', views.textToSpeech, name='cashierTextToSpeech'),
]