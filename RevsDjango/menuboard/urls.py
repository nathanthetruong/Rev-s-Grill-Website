from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_board, name='Revs-Menuboard-Screen'),
]