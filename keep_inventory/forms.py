from django import forms
from .models import StockIn, StockOut


class StockInForm(forms.ModelForm):
    """Form for stock-in"""
    class Meta:
        model = StockIn
        fields = "__all__"
        exclude = ['user', 'date',]
        widgets = {
            'sku':forms.TextInput(
                attrs={'autocomplete':'sku'}
            ),
            
            'closest_expiry_date':forms.DateInput(
                attrs={'placeholder': 'Year-Month-Day'}
                ),

            'expiring_soon_alert_date':forms.DateInput(
                attrs={'placeholder': 'Year-Month-Day'}
                ),
        }

    def clean_input(self):
        name = self.cleaned_data['product_name']
        return name.title()

class StockOutForm(forms.ModelForm):
    """Form for stock-out"""
    class Meta:
        model = StockOut
        fields = "__all__"
        exclude = ['user', 'date',]

    def clean_input(self):
        name = self.cleaned_data['product_name']
        return name.title()
