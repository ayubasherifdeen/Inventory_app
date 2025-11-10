from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from . models import Product


# Create your views here.
def index(request):
    """The home page of inventory"""
    return render(request, 'keep_inventory/index.html')


def search_products(request):
    query = request.GET.get('q', '')
    results = []
    cart = request.session.get('cart', [])

    if query:
        results = Product.objects.filter(product_name__icontains=query)

    context = {
        'query': query,
        'results': results,
        'cart': cart,
    }
    return render(request, 'keep_inventory/sell.html', context)


def add_to_cart(request):
    """Add to cart"""
    #check post method and request session
    if request.method=="POST":
        product_id = request.POST.get('product_id')
        quantity =int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', [])

        if not product_id:
            return redirect('keep_inventory:sell')

        product = get_object_or_404(Product, product_id=product_id)

        #check if an item has already been added or not
        for item in cart:
           if item['product_id'] == str(product.product_id):
               item['quantity'] += quantity
               item['amount'] = float(product.unit_selling_price) * item['quantity']
               break
        else:
            cart.append({
            'product_id': str(product.product_id),
            'product_name': product.product_name,
            'unit_selling_price': float(product.unit_selling_price),
            'quantity': quantity,
            'amount': float(product.unit_selling_price) * quantity,
                })
        #update cart session
        request.session['cart'] = cart
        return redirect('keep_inventory:sell')
    
    return redirect('keep_inventory:sell')










   




