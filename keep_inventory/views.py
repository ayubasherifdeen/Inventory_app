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

def register(request):
    """Register a new user"""
    if request.method !='POST':
        #Display new registration form
        new_registration_form = UserCreationForm()
    else:
        #Process complete form
        new_registration_form = UserCreationForm(request.POST)

        if new_registration_form.is_valid():
            new_user = new_registration_form.save()
            #log the user in and redirect to homepage
            login(request,new_user)
            return redirect('keep_inventory:index')
        
    #Display a blank or invalid form
    context = {'new_registration_form':new_registration_form}
    return render(request, 'registration/register.html', context)