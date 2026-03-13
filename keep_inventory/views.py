from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from . models import Product, Sale, SalesDetail
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.contrib import messages
from django.db.models import Count, Sum
from datetime import timedelta, date, datetime
from django.http import JsonResponse
from .forms import StockInForm, StockOutForm
from .utils import *


# Create your views here.
@login_required
def index(request):
    """Home page – automatically loads today's sales."""
    
    # Default: today's date range
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Auto-query for today's sales
    sales_count = Sale.objects.filter(
        sales_date__range=(today, tomorrow),
        owner=request.user
    ).count()

    total_sales = Sale.objects.filter(
        sales_date__range=(today, tomorrow),
        owner=request.user
    ).aggregate(total=Sum('total_amount'))['total']

    #check for shortages
    low_stock = Product.objects.filter(
        total_stock__lte=F('shortage_threshold')
    ).values('product_name', 'total_stock')

    #check for expiry
    expiring_soon = check_expiring_soon(request)
    expiring_today = check_expiring_today(request)
    expired = check_expired(request)


    # Check if search view passed custom dates via session
    start_date = request.session.pop('start_date', today)
    end_date = request.session.pop('end_date', tomorrow)
    sales_count = request.session.pop('sales_count', sales_count)
    total_sales = request.session.pop('total_sales', total_sales)

    return render(request, 'keep_inventory/index.html', {
        'sales_count': sales_count,
        'total_sales': total_sales,
        'start_date': start_date,
        'end_date': end_date,
        'low_stock':low_stock,
        'expiring_soon':expiring_soon,
        'expiring_today':expiring_today,
        'expired':expired,
        'auto_load': True,
    })


@login_required
def search_sales_per_date(request):
    """Search sales per date and store aggregates in session"""
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    
    start_date, end_date = get_date(start_date_str, end_date_str)
    
    if not start_date:
        return redirect('keep_inventory:index')
    
    sales = get_sales(request.user, start_date, end_date)
    
    sales_count = sales.count()
    total_sales = sales.aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Store in session
    request.session['start_date'] = str(start_date)
    request.session['end_date'] = str(end_date)
    request.session['sales_count'] = sales_count
    request.session['total_sales'] = str(total_sales)
    
    return redirect('keep_inventory:index')


@login_required
def search_transaction_per_date(request):
    """Search transactions per date and display them"""
    start_date_str = request.GET.get('start_date_tr')
    end_date_str = request.GET.get('end_date_tr')
    
    # Parse dates (use today if empty)
    start_date, end_date = get_date(
        start_date_str, 
        end_date_str, 
        use_today_if_empty=True
    )
    
    # Get transactions
    if start_date:
        transactions = get_sales(request.user, start_date, end_date)
    else:
        transactions = None
    
    return render(request, "keep_inventory/transactions.html", {
        'start_date': start_date,
        'end_date': end_date,
        'transactions': transactions,
        'auto_load': True
    })

    
    

@login_required
def search_products(request):
    """Search products"""
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
        sku = request.POST.get('sku')
        quantity =int(request.POST.get('quantity', 1))
        cart = request.session.get('cart', [])
        
        if not sku:
            return redirect('keep_inventory:sell')

        product = get_object_or_404(Product, sku=sku)

        #check if an item has already been added or not
        for item in cart:
           if item['sku'] == product.sku:
               item['quantity'] += quantity
               item['amount'] = float(product.unit_selling_price) * item['quantity']
               break
        else:
            cart.append({
            'sku': str(product.sku),
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


def remove_from_cart(request, sku):
    """Remove a selected item from cart"""
    cart =request.session.get('cart', [])
     # Filter out the product you want to remove
    updated_cart = [item for item in cart if item['sku'] != sku]

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
                product = Product.objects.get(sku=item['sku'])

                items.append({
                    "sku": str(product.sku),
                    "product_name": product.product_name,
                    "quantity": item['quantity'],
                    "unit_price": float(item['unit_selling_price']),
                    "amount": float(item['amount']),
                })

                total_quantity += item['quantity']

                # Reduce stock
                Product.objects.filter(sku=product.sku).update(
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

    except Exception:
        # If something breaks, rollback automatically
        return redirect("keep_inventory:sell")

    return redirect("keep_inventory:sell")




def sale_details_api(request, sale_id):
    sale = get_object_or_404(
        Sale.objects.select_related('salesdetail'),
        sales_id=sale_id,
        owner=request.user
    )
    
    if not hasattr(sale, 'salesdetail'):
        return JsonResponse({"error": "Details not found"}, status=404)
    
    return JsonResponse({
        "sale_date": sale.sales_date.strftime("%Y-%m-%d %H:%M"),
        "total_amount": str(sale.total_amount),
        "items": sale.salesdetail.items,
    })


@login_required
def stock_in(request):
    """
    Add  products.
    """
    if request.method == 'POST':
        stock_in_form = StockInForm(request.POST)
        
        if stock_in_form.is_valid():
            stock_in_record=stock_in_form.save(commit=False)
            stock_in_record.user = request.user
            product = stock_in_record.sku
            stock_in_record.save()
            messages.success(request, f'{product.product_name} added successfully!')
            return redirect('keep_inventory:stock_in')
    else:
        stock_in_form = StockInForm()
    
    return render(
        request, 
        'keep_inventory/stock_in.html', 
        {'form': stock_in_form}
    )


@login_required
def stock_out(request):
    """
    Remove stock from products.
    """
    if request.method == 'POST':
        stock_out_form = StockOutForm(request.POST)
        
        if stock_out_form.is_valid():
            stock_out_record = stock_out_form.save(commit=False)
            stock_out_record.user = request.user
            product = stock_out_record.sku
            stock_out_record.save()
            messages.success(
                request, 
                f'{product.product_name} stock removed successfully!'
            )
            return redirect('keep_inventory:stock_out')
    else:
        
        stock_out_form = StockOutForm()
    
    return render(
        request, 
        'keep_inventory/stock_out.html', 
        {'form': stock_out_form}
    )



#Admin dashboard
def dashboard_callback(request, context):

        
    context.update({
        "custom_variable": "value",
    })

    return context