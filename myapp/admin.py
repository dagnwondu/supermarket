from django.contrib import admin
from .models import Product, StockHistory, Sale, DailySummary, Category


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'selling_price', 'buying_price', 'expiry_date', 'is_expired')
    list_filter = ('category', 'expiry_date')
    search_fields = ('name', 'barcode')
    ordering = ('name',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
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
