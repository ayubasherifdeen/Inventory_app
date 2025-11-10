from django.contrib import admin
from .models import Product, Sale, SalesDetail

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display=['product_name','unit_cost_price', 'unit_selling_price','unit_profit', 'total_stock','total_profit' ]
    readonly_fields = ['quantity_in_stock','unit_profit','total_stock','total_profit', ]
    
admin.site.register(Sale)
admin.site.register(SalesDetail)

# Register your models here.
