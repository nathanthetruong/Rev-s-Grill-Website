from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def menu_board(request):
    return render(request, 'menuboard/menuboard.html')
