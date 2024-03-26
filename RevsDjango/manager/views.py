from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def manager(request):
    return render(request, 'manager/manager.html')
