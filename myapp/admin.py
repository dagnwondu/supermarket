from django.contrib import admin
from .models import Category, Product, Stock, Sale, DailySummary, SaleItem
from django.db.models import Sum

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

# @admin.register(Sale)
# class SaleAdmin(admin.ModelAdmin):
#     list_display = ('product', 'quantity', 'total_price', 'created_at')
#     list_filter = ('product', 'created_at')

@admin.register(DailySummary)
class DailySummaryAdmin(admin.ModelAdmin):
    list_display = ('date', 'total_sales', 'total_items_sold')
    ordering = ('-date',)
class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 1
    readonly_fields = ('total_price',)
    autocomplete_fields = ['product']

@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'total_price', 'total_quantity')
    readonly_fields = ('total_price',)
    inlines = [SaleItemInline]

    def total_quantity(self, obj):
        return obj.items.aggregate(total=Sum('quantity'))['total'] or 0
    total_quantity.short_description = "Total Quantity"