from django.contrib import admin
from .models import Product, Sale, SalesDetail


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['product_name','unit_cost_price', 'unit_selling_price','unit_profit', 'total_stock','total_profit' ]
    readonly_fields = ['quantity_in_stock','unit_profit','total_stock','total_profit', ]
    
@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display=['sales_id','owner', 'sales_date', 'total_amount']
    readonly_fields=['sales_id', 'owner', 'sales_date', 'total_amount']

@admin.register(SalesDetail)
class SalesDetailAdmin(admin.ModelAdmin):
    list_display=['sales_detail_id']
    readonly_fields=['sales_detail_id', 'sales_id', 'product_id', 'product_name','unit_price', 'quantity', 'amount']


# Register your models here.
