from django.shortcuts import render

# Create your views here.
def cashier(request):
    return render(request, 'cashier/cashier.html')
