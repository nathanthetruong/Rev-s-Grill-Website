from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def orders(request):
    return render(request, 'orders/orders.html')
