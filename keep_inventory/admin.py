from django.contrib import admin
from .models import Product, Sale, SalesDetail


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['product_name','unit_cost_price', 'unit_selling_price','unit_profit', 'total_stock','total_profit' ]
    readonly_fields = ['unit_profit','total_stock','total_profit', ]
    search_fields = ('product_name',)

    

    
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display=['sales_id','owner', 'sales_date', 'total_amount',]
    readonly_fields=['sales_id', 'owner', 'sales_date', 'total_amount']

@admin.register(SalesDetail)
class SalesDetailAdmin(admin.ModelAdmin):
    list_display = ['sales_id', 'total_quantity', 'total_amount', 'created_at']
    readonly_fields = ("formatted_items",)
    fieldsets = (
        ("Items Purchased", {
            "fields": ("formatted_items",),
        }),
    )


# Register your models here.
