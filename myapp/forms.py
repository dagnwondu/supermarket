from django import forms
from .models import Category, Product, Stock, Sale, SaleItem
from django.core.exceptions import ValidationError
from datetime import date

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description']

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'category', 'barcode', 'selling_price']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter product name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
            'barcode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Optional barcode'
            }),
            'selling_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'placeholder': 'Selling price'
            }),
        }
class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        fields = [ 'buying_price', 'batch_number', 'expiry_date']

# class SaleForm(forms.ModelForm):
#     class Meta:
#         model = Sale

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Show only products that have stock
#         self.fields['product'].queryset = Product.objects.all()
#         self.fields['quantity'].widget.attrs.update({'min': '1', 'class': 'form-control'})
#         self.fields['product'].widget.attrs.update({'class': 'form-select'})

#     def clean_quantity(self):
#         quantity = self.cleaned_data['quantity']
#         product = self.cleaned_data.get('product')
#         if product:
#             total_stock = product.total_stock
#             if quantity > total_stock:
#                 raise ValidationError(f"Only {total_stock} units of {product.name} are available in stock.")
#         return quantity
class SaleItemForm(forms.ModelForm):
    class Meta:
        model = SaleItem
        fields = ['product', 'quantity', 'selling_price']
        widgets = {
            'product': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'selling_price': forms.NumberInput(attrs={'class': 'form-control', 'step': 0.01}),
        }

class SaleForm(forms.ModelForm):
    class Meta:
        model = Sale
        fields = []  # No editable fields; total_price is auto-calculated