from django.contrib import admin
from .models import Product, Sale, SalesDetail,StockAdjustment
import django.apps



@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['sku','product_name','unit_cost_price', 'unit_selling_price'
                  ,'unit_profit', 'total_stock','total_profit',
                    'closest_expiry_date']
    readonly_fields = ['unit_profit','total_stock','total_profit', ]
    search_fields = ['product_name']

    
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display=['sales_id','owner', 'sales_date', 'total_amount',]
    readonly_fields=['sales_id', 'owner', 'sales_date', 'total_amount']
    list_filter = ['sales_date', 'owner']
 

@admin.register(SalesDetail)
class SalesDetailAdmin(admin.ModelAdmin):
    list_display = ['sales_detail_id','sales_id', 'total_quantity', 'total_amount']
    readonly_fields = ("formatted_items",)
    
    
    fieldsets = (
        ("Items Purchased", {
            "fields": ("formatted_items",),
        }),
    )


@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'quantity', 'reason', 'date', 'user']
    readonly_fields = ['product_name', 'quantity', 'reason', 'date', 'user']
    list_filter = ['product_name', 'reason', 'date', 'user']


