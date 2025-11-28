from django.contrib import admin
from .models import Product, StockHistory, Sale, DailySummary


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'quantity', 'expiry_date')
    list_filter = ('category', 'expiry_date')
    search_fields = ('name', 'barcode')
    ordering = ('name',)


@admin.register(StockHistory)
class StockHistoryAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_added', 'date_added', 'expiry_date')
    list_filter = ('date_added', 'expiry_date')
    search_fields = ('product__name',)
    ordering = ('-date_added',)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity_sold', 'price_each', 'total_price', 'date_sold')
    list_filter = ('date_sold',)
    search_fields = ('product__name',)
    ordering = ('-date_sold',)


@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_items_sold')
    ordering = ('-date',)
