from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StockIn, StockOut, Product
from django.db.models import F

@receiver(post_save, sender=StockIn)
def update_with_stock_in(sender, instance, created, **kwargs):
    """update or create product according to StockIn"""
    if created:
        Product.objects.update_or_create(
            sku = instance.sku,
            defaults={
            'product_name' :instance.product_name,
            'unit_cost_price' : instance.unit_cost_price,
            'unit_selling_price' : instance.unit_selling_price,
            'total_stock': F('total_stock') + instance.stock if 'total_stock' in Product._meta.get_fields() else instance.stock,
            'shortage_threshold' : instance.shortage_threshold,
            'closest_expiry_date' : instance.closest_expiry_date if 'closest_expiry_date' < Product._meta.get_fields() else instance.closest_expiry_date,
            }
        )


@receiver(post_save, sender=StockOut)
def update_with_stock_out(sender, instance, created, **kwargs):
    """update with stockout"""
    if created:
        Product.objects.update(
            product = instance.sku,
            defaults={
                'total_stock': F('total_stock') - instance.stock if 'total_stock' in Product._meta.get_fields() and instance.stock < F('total_stock') else instance.stock,
            }
        )
