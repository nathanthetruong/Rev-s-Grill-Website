import json
from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse, JsonResponse
from django.db import connection

def administrator(request):
    return render(request, 'administrator/administrator.html')