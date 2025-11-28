from django import forms
from .models import Product, StockHistory, Sale

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'barcode', 'buying_price', 'selling_price', 'expiry_date']

class StockForm(forms.ModelForm):
    class Meta:
        model = StockHistory
        fields = ['product', 'quantity_added', 'expiry_date']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity_added': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'expiry_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = ['product', 'quantity_sold']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-select'}),
            'quantity_sold': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }
