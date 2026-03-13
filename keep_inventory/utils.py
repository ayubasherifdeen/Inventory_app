from .models import Product, Sale
from datetime import timedelta, date, datetime, time
from dateutil.relativedelta import relativedelta


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


def get_date(start_date_str, end_date_str, use_today_if_empty=False):
    """Get date for queries"""
    # Handle empty dates
    if not start_date_str and not end_date_str:
        if use_today_if_empty:
            today = date.today()
            return today, today
        return None, None
    
    # Both must be provided if one is
    if not start_date_str or not end_date_str:
        return None, None
    
    # Parse dates
    try:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        return start_date, end_date
    
    except ValueError:
        return None, None


def get_sales(user, start_date, end_date):
    """Query for sales within range"""
    end_date_next = end_date + timedelta(days=1)
    
    return Sale.objects.filter(
        sales_date__range=(start_date, end_date_next),
        owner=user
    ).order_by('-sales_date')
