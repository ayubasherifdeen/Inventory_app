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
from dateutil.relativedelta import relativedelta
from django.http import JsonResponse

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
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    if not start_date_str or not end_date_str:
        # Missing dates → redirect with no session overrides
        return redirect('keep_inventory:index')

    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

        # Adjust end date for range filtering
        end_date_next = end_date + timedelta(days=1)

        # Query
        sales_count = Sale.objects.filter(
            sales_date__range=(start_date, end_date_next),
            owner=request.user
        ).count()

        total_sales = Sale.objects.filter(
            sales_date__range=(start_date, end_date_next),
            owner=request.user
            ).aggregate(total=Sum('total_amount'))['total']

        # Store results in session
        request.session['start_date'] = str(start_date)
        request.session['end_date'] = str(end_date)
        request.session['sales_count'] = sales_count
        request.session['total_sales'] = total_sales

    except ValueError:
        pass

    return redirect('keep_inventory:index')







@login_required
def search_transaction_per_date(request):
    start_date_str = request.GET.get('start_date_tr')
    end_date_str = request.GET.get('end_date_tr')

    # Validate input
    transactions = None
    if not start_date_str and not end_date_str:
         # Get today's date
        today = date.today()
        tomorrow = today + timedelta(days=1)

         # Convert strings to date objects
        start_date = today
        end_date = tomorrow

        # query and count number of sales
        transactions = Sale.objects.filter(
            sales_date__range=(start_date, end_date),
            owner=request.user
        ).order_by('-sales_date')

    if start_date_str and end_date_str:
       
        #If date is provided
        try:
            # Convert strings to date objects
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

            # query and count number of sales
            transactions = Sale.objects.filter(
                sales_date__range=(start_date, end_date),
                owner=request.user
            ).order_by('-sales_date')
  
        except ValueError:
            transactions = None

    

    return render(request, "keep_inventory/transactions.html", context = {

        'start_date':start_date,
        'end_date':end_date,
        'transactions':transactions,
        'auto_load':True
    })

    
    

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
        # If something breaks, rollback happens automatically
        return redirect("keep_inventory:sell")

    return redirect("keep_inventory:sell")


def check_expiring_soon(request):
    """Check for products expiring within the next month"""
    today = date.today()
    three_months_from_now = today + relativedelta(months=3)
    return list(
        Product.objects.filter(
        closest_expiry_date__lt = three_months_from_now,
        closest_expiry_date__gte=today 
        ).values('product_name','closest_expiry_date' )
    )

def check_expiring_today(request):
    """Check for products expiring today"""
    today = date.today()

    return list(
        Product.objects.filter(
        closest_expiry_date = today
        ).values('product_name','closest_expiry_date' )
    )

def check_expired(request):
    """Check for products whose expiring dates have elapsed"""
    today = date.today()

    return list(
        Product.objects.filter(
        closest_expiry_date__lt = today
        ).values('product_name','closest_expiry_date' )
    )



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
















   




