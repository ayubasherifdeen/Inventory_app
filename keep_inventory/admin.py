
from django.db.models import Sum, Count, Avg
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from unfold.admin import ModelAdmin

from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from .models import Product, Sale, SalesDetail, StockIn, StockOut

from unfold.contrib.filters.admin import RangeDateFilter
import django.apps



#user and authentications
admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    # Forms loaded from `unfold.forms`
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm


@admin.register(Group)
class GroupAdmin(BaseGroupAdmin, ModelAdmin):
    pass



#created models
@admin.register(Product)
class ProductAdmin(ModelAdmin):
    list_display=['sku','product_name','unit_cost_price', 'unit_selling_price'
                  ,'unit_profit', 'total_stock','total_profit',
                    'closest_expiry_date']
    readonly_fields = ['unit_profit','total_stock','total_profit', ]
    search_fields = ['product_name']
    list_per_page = 25

    

    # Warn before leaving unsaved changes in changeform
    warn_unsaved_form = True  # Default: False

    
@admin.register(Sale)
class SaleAdmin(ModelAdmin):
    list_display=['sales_id','owner', 'sales_date', 'total_amount',]
    readonly_fields=['sales_id', 'owner', 'sales_date', 'total_amount']
    list_filter = (('sales_date', RangeDateFilter), 'owner')
    list_filter_submit = True 
    list_per_page = 25
 

@admin.register(SalesDetail)
class SalesDetailAdmin(ModelAdmin):
    list_display = ['sales_detail_id','sales_id', 'total_quantity', 'total_amount']
    readonly_fields = ("formatted_items",)
    list_per_page = 25
    
    fieldsets = (
        ("Items Purchased", {
            "fields": ("formatted_items",),
        }),
    )


@admin.register(StockIn)
class StockInAdmin(ModelAdmin):
    list_display=['stock_in_ID','user', 'sku', 'product_name', 'unit_cost_price', 'unit_selling_price', 'stock','date']
    readonly_fields=['stock_in_ID','sku','user','product_name','unit_cost_price', 'unit_selling_price', 'stock','shortage_threshold', 'closest_expiry_date', 'date']
    list_filter=['user', ('date', RangeDateFilter)]
    list_filter_submit = True 
    list_per_page = 25


@admin.register(StockOut)
class StockOutAdmin(ModelAdmin):
    list_display=['stock_out_ID', 'user', 'sku', 'product_name', 'stock', 'reason', 'date']
    readonly_fields=['stock_out_ID', 'user', 'sku', 'product_name', 'stock', 'reason', 'date']
    list_filter=['user', 'reason', ('date', RangeDateFilter)]
    list_filter_submit = True 
    list_per_page = 25





