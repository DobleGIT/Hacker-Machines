from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
	return render(request, 'accounts/home.html')

def products(request):
	return HttpResponse('products')

def customer(request):
	return HttpResponse('customer')
# Create your views here.
