from django.contrib import admin
from .models import Category, Product, Stock, Sale, DailySummary

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'total_stock')
    list_filter = ('category',)
    search_fields = ('name', 'barcode')

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'buying_price', 'batch_number', 'expiry_date', 'added_at', 'is_expired')
    list_filter = ('product', 'expiry_date')
    search_fields = ('product__name', 'batch_number')

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'total_price', 'created_at')
    list_filter = ('product', 'created_at')

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_items_sold')
    ordering = ('-date',)
