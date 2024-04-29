from django.urls import path
from . import views

'''
This is the order page routing logic.
'''

urlpatterns = [
    path('', views.orders, name='Revs-Order-Screen'),
    path('', views.orders, name='Revs-Menu-Screen'),
    path('checkout/', views.checkout, name='checkout'),
    path('add/', views.addItem, name='addItem'),
    path('transaction/', views.transactionView, name='transaction'),
    path('orders/', views.transactionView, name='orders'),
    path('getCartItems/', views.getCartItems, name='getCartItems'),
    path('login/', views.loginView, name='login'),
    path('removeItem/', views.removeItem, name='removeItem'),
    path('removeAllIems/', views.removeAllIems, name='removeAllItems'),
    path('textToSpeech/', views.textToSpeech, name='textToSpeech'),
]