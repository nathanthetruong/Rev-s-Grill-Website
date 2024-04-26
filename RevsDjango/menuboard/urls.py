from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_board, name='Revs-Menuboard-Screen'),
    # path('orders/', views.orders, name='Revs-Order-Screen'),  # Add orders view and url pattern
    # path('login/', views.login, name='Revs-Login-Screen'),  # Add login view and url pattern
    path('help/', views.help, name='help'),
]