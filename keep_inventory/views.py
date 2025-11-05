from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from . models import Product

# Create your views here.
def index(request):
    """The home page of inventory"""
    return render(request, 'keep_inventory/index.html')

def search_products(request):
    query = request.GET.get('q', '')  # 'q' is the name of the input box
    results = []

    if query:
        results = Product.objects.filter(product_name__icontains=query)  # case-insensitive search

    context = {
        'query': query,
        'results': results,
    }
    return render(request, 'keep_inventory/sell.html', context)

