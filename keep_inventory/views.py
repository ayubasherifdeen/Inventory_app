from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from . models import Product, Sale, SalesDetail
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.contrib import messages
from django.db.models import Count
from datetime import timedelta
from datetime import datetime

# Create your views here.
def index(request):
    """The home page of inventory"""
    sales_count = request.session.pop('sales_count', None)

    return render(request, 'keep_inventory/index.html', {
        'sales_count': sales_count
    })


@login_required
def search_transaction_per_date(request):
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    # Validate input
    if not start_date_str or not end_date_str:
        request.session['sales_count'] = None
        return redirect('keep_inventory:index')

    try:
        # Convert strings to date objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # query and count number of sales
        sales_count = Sale.objects.filter(
            sales_date__range=(start_date, end_date),
            owner=request.user
        ).count()

        # Store in session so index page can access it
        request.session['sales_count'] = sales_count

    except ValueError:
        # Invalid date format
        request.session['sales_count'] = None

    return redirect('keep_inventory:index')




    

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
        request.session['total_amount'] = float(total_amount)

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
    if request.method != "POST":
        return redirect("keep_inventory:sell")

    cart = request.session.get('cart', [])
    total_amount = request.session.get('total_amount', 0)

    if not cart:
        return redirect("keep_inventory:sell")

    try:
        with transaction.atomic():
            # Create Sale record
            sale = Sale.objects.create(
                total_amount=total_amount,
                owner=request.user
            )

            # Prepare items list and update stock
            items = []
            total_quantity = 0

            for item in cart:
                product = Product.objects.get(product_id=item['product_id'])

                items.append({
                    "product_id": str(product.product_id),
                    "product_name": product.product_name,
                    "quantity": item['quantity'],
                    "unit_price": float(item['unit_selling_price']),
                    "amount": float(item['amount']),
                })

                total_quantity += item['quantity']

                # Reduce stock
                Product.objects.filter(product_id=product.product_id).update(
                    total_stock=F('total_stock') - item['quantity']
                )

            # Create SalesDetail record
            SalesDetail.objects.create(
                sales_id=sale,
                items=items,
                total_quantity=total_quantity,
                total_amount=total_amount
            )

            # Clear session
            request.session['cart'] = []
            request.session['total_amount'] = 0

            messages.success(request, f"Cart cleared, sale succesful")

    except Exception:
        # If something breaks, rollback happens automatically
        return redirect("keep_inventory:sell")

    return redirect("keep_inventory:sell")
















   




