from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import StockIn, StockOut, Product
from django.db.models import F, Case, When, Q
from django.db import models
@receiver(post_save, sender=StockIn)
def update_with_stock_in(sender, instance, created, **kwargs):
    """update or create product according to StockIn"""
    if created:
        Product.objects.update_or_create(
            sku=instance.sku,
            defaults={
                'product_name': instance.product_name,
                'unit_cost_price': instance.unit_cost_price,
                'unit_selling_price': instance.unit_selling_price,
                'shortage_threshold': instance.shortage_threshold,
                # Handle total_stock: increment if exists, else set to instance.stock
                'total_stock': Case(
                    When(Q(total_stock__isnull=False), then=F('total_stock') + instance.stock),
                    default=instance.stock,
                    output_field=models.PositiveIntegerField(),
                ),
                # Handle closest_expiry_date: take the earlier (min) date
                'closest_expiry_date': Case(
                    When(Q(closest_expiry_date__isnull=False) & Q(closest_expiry_date__lt=instance.closest_expiry_date),
                         then=F('closest_expiry_date')),
                    default=instance.closest_expiry_date,
                    output_field=models.DateTimeField()
                ),
            }
        )


@receiver(post_save, sender=StockOut)
def update_with_stock_out(sender, instance, created, **kwargs):
    if created:
        Product.objects.update_or_create(
            sku=instance.sku,
            defaults={
                'total_stock': Case(
                    When(total_stock__isnull=False, then=F('total_stock') - instance.stock),
                    default=0,
                    output_field=models.PositiveIntegerField(),
                )
            }
        )
