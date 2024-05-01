from django.urls import path
from . import views

urlpatterns = [
    path('', views.menu_board, name='Revs-Menuboard-Screen'),

    path('help/', views.help, name='Revs-Help-Screen'),
]
