from django import forms
from .models import StockIn, StockOut





class StockMovementForm(forms.Form):
    CHOICES = [
        ('add_product', 'Add Product'),
        ('remove_product', 'Remove Product'),
       
    ]
    choice = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect(),
    )

class StockInForm(forms.ModelForm):
    """Form for stock-in"""
    class Meta:
        model = StockIn
        fields = "__all__"
        exclude = ['user', 'date',]

class StockOutForm(forms.ModelForm):
    """Form for stock-out"""
    class Meta:
        model = StockOut
        fields = "__all__"
        exclude = ['user', 'date',]