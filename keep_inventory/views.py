from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from . models import Product, Sale, SalesDetail
from django.db import transaction
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    """The home page of inventory"""
    return render(request, 'keep_inventory/index.html')

@login_required
def search_products(request):
    query = request.GET.get('q', '')
    results = []
    cart = request.session.get('cart', [])
    total_amount = request.session.get('total_amount', 0)


    if query:
        results = Product.objects.filter(product_name__icontains=query)

    context = {
        'query': query,
        'results': results,
        'cart': cart,
        'total_amount': total_amount
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
            
            #calculate total amount for all items
            total_amount = sum(item['amount'] for item in cart)

        #update cart session
        request.session['cart'] = cart
        request.session['total_amount'] = total_amount

        return redirect('keep_inventory:sell')
    
    return redirect('keep_inventory:sell')


def remove_from_cart(request, product_id):
    """Remove a selected item from cart"""
    cart =request.session.get('cart', [])
     # Filter out the product you want to remove
    updated_cart = [item for item in cart if item['product_id'] != product_id]

    #recalculate cart total
    total_amount = sum(item['amount'] for item in updated_cart)

    # Update session
    request.session['cart'] = updated_cart
    request.session['total_amount'] = total_amount  

    # Redirect back to the sell page
    return redirect('keep_inventory:sell')


@transaction.atomic
def confirm_sale(request):
    """Confirm sale and checkout cart"""
    if request.method == "POST":
        cart = request.session.get('cart', [])
        total_amount = request.session.get('total_amount', 0)

        if not cart:
            redirect("keep_inventory:sell")

    #Create sale record
    sale = Sale.objects.create(total_amount=total_amount)

    #Create sale detail for each item
    for item in cart:
        product = Product.objects.get(product_id=item['product_id'])
        
        SalesDetail.objects.create(
            sales_id=sale,
            product_id=product,
            product_name=product.product_name,
            quantity=item['quantity'],
            unit_price=item['unit_selling_price'],
            amount=item['amount'],
            )
        
        #make update stock quantity
        product.total_stock = product.total_stock - item['quantity']
        product.save()

        request.session['cart'] = []
        request.session['total_amount'] = 0

        #Redirect back to the sell page
        return redirect('keep_inventory:sell')

    return redirect('keep_inventory:sell')














   




