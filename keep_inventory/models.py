from django.db import models
from django.db.models import F
import uuid
from django.contrib.auth.models import User
from django.db.models import JSONField
from django.utils.safestring import mark_safe
from phonenumber_field.modelfields import PhoneNumberField



class Product(models.Model):
    """A product sold by the shop"""
    sku = models.CharField(primary_key=True, max_length=15)
    product_name = models.CharField(max_length=200)
    unit_cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)

    # Now represents current stock
    total_stock = models.IntegerField(null=True, default=0)  
    # Temporary field for new stock additions
    add_stock = models.PositiveIntegerField(null=True, default=0)
    reduce_stock = models.PositiveIntegerField(null=True, default=0)     

    def save(self, *args, **kwargs):
        # Update current stock before saving
        if self.add_stock:
            self.total_stock = (self.total_stock or 0) + self.add_stock
            self.add_stock = 0  # Reset after applying
        if self.reduce_stock:
            self.total_stock = (self.total_stock or 0) - self.reduce_stock
            self.reduce_stock = 0
        super().save(*args, **kwargs)

    @property
    def unit_profit(self):
        if self.unit_cost_price is not None and self.unit_selling_price is not None:
            return self.unit_selling_price - self.unit_cost_price
        return None

    @property
    def total_profit(self):
        profit = self.unit_profit
        if profit is not None and self.total_stock is not None:
            return profit * self.total_stock
        return None

    def __str__(self):
        return self.product_name
    
    shortage_threshold = models.IntegerField(null=False, default=1)
    closest_expiry_date = models.DateField(null=True, default=None, blank=True)
    expiring_soon_alert_date = models.DateField(null=True, blank=True, default=None)
    

class Sale(models.Model):
    """A sale made"""
    sales_id=models.BigAutoField(primary_key=True, editable=False)
    sales_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    
class SalesDetail(models.Model):
    """Details of a sales made"""
    sales_detail_id=models.BigAutoField(primary_key=True)
    sales_id = models.OneToOneField(Sale, related_name="salesdetail", on_delete=models.CASCADE)
    items = models.JSONField()  # Stores list of products sold in one transaction
    total_quantity = models.IntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def formatted_items(self):
        """Return items as a neat HTML table for admin display."""
        if not self.items:
            return "-"

        html = """
        <table style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background: #f2f2f2;">
                <th style="border: 1px solid #ccc; padding: 6px;">SKU</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Product</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Qty</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Price</th>
                <th style="border: 1px solid #ccc; padding: 6px;">Subtotal</th>
            </tr>
        </thead>
        """

        for item in self.items:
            html += f"""
            <tbody>
            <tr>
                <td style="border: 1px solid #ccc; padding: 6px;">{item['sku']}</td>
                <td style="border: 1px solid #ccc; padding: 6px;">{item['product_name']}</td>
                <td style="border: 1px solid #ccc; padding: 6px; text-align: center;">{item['quantity']}</td>
                <td style="border: 1px solid #ccc; padding: 6px;">{item['unit_price']}</td>
                <td style="border: 1px solid #ccc; padding: 6px;">{item['amount']}</td>
            </tr>
            </tbody>
            """

        html += "</table>"
        return mark_safe(html)

    formatted_items.short_description = "Items Purchased"

    def __str__(self):
        return f"Sale Details #{self.sales_detail_id}"


class StockAdjustment(models.Model):
    """Manuel adjustments to stock made in user's site"""
    sku = models.ForeignKey(Product,on_delete=models.CASCADE)
    product_name =models.CharField(max_length=200)
    quantity = models.IntegerField()
    reason = models.CharField()
    date = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)



    






