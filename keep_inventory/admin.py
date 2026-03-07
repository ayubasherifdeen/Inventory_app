from django.contrib import admin
from .models import Product, Sale, SalesDetail, StockIn, StockOut
from rangefilter.filters import DateRangeFilter
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
    list_filter = [('sales_date', DateRangeFilter), 'owner']
 

@admin.register(SalesDetail)
class SalesDetailAdmin(admin.ModelAdmin):
    list_display = ['sales_detail_id','sales_id', 'total_quantity', 'total_amount']
    readonly_fields = ("formatted_items",)
    
    
    fieldsets = (
        ("Items Purchased", {
            "fields": ("formatted_items",),
        }),
    )


@admin.register(StockIn)
class StockInAdmin(admin.ModelAdmin):
    list_display=['stockInID','user', 'sku', 'product_name', 'unit_cost_price', 'unit_selling_price', 'stock','date']
    readonly_fields=['stockInID','sku','user','product_name','unit_cost_price', 'unit_selling_price', 'stock','shortage_threshold', 'closest_expiry_date', 'date']
    list_filter=['user', ('date', DateRangeFilter)]


@admin.register(StockOut)
class StockOutAdmin(admin.ModelAdmin):
    list_display=['stockOutID', 'user', 'sku', 'product_name', 'stock', 'reason', 'date']
    readonly_fields=['stockOutID', 'user', 'sku', 'product_name', 'stock', 'reason', 'date']
    list_filter=['user', 'reason', ('date', DateRangeFilter)]





