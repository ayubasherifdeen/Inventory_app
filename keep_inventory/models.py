from django.db import models
from django.db.models import F
import uuid

class Product(models.Model):
    """A product sold by the shop"""
    product_id=models.IntegerField(primary_key=True, default=uuid.uuid4)
    product_name = models.CharField(max_length=200)
    unit_cost_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    unit_selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)
    unit_profit = models.GeneratedField(
        expression = F('unit_selling_price') - F('unit_cost_price'),
        output_field = models.DecimalField(max_digits=10, decimal_places=2),
        db_persist=True
    )
    add_stock = models.IntegerField(null=True, default=0)
    quantity_in_stock = models.IntegerField(null=True, default=0)
    total_stock = models.GeneratedField(
        expression = F('add_stock')+F('quantity_in_stock'),
        output_field = models.IntegerField(null=True),
        db_persist =True
    )
    total_profit = models.GeneratedField(
        expression = F('unit_profit') * F('quantity_in_stock'),
        output_field = models.DecimalField(max_digits=10, decimal_places=2),
        db_persist =True
    )

    

    def __str__(self):
        """Return a string representation of the model"""
        return self.product_name


class Sale(models.Model):
    """A sale made"""
    sales_id=models.BigIntegerField(primary_key=True, default=uuid.uuid4)
    sales_date = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None)

class SalesDetail(models.Model):
    """Details of a sales made"""
    sales_detail_id=models.BigIntegerField(primary_key=True, default=uuid.uuid4)
    sales_id = models.ForeignKey(Sale, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)   
    unit_price =models.DecimalField(max_digits=10, decimal_places=2, null=True, default=None) 
    quantity = models.IntegerField(null=True, default=None)
    



