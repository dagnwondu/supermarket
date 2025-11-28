from django.db import models
from datetime import date

# =========================
# CATEGORY
# =========================
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


# =========================
# PRODUCT
# =========================

class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # retail price
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_stock(self):
        return self.batches.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def low_stock(self):
        """Optional: flag for low stock if you want."""
        return self.total_stock < 10  # example threshold


class Stock(models.Model):
    product = models.ForeignKey(Product,related_name="batches", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"

    def is_expired(self):
        """Return True if this stock batch is expired."""
        return self.expiry_date and self.expiry_date < date.today()


# =========================
# SALE (optional for customer sales)
# =========================
class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total_price = models.DecimalField(max_digits=10, decimal_places=2)  # selling_price * quantity
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale: {self.product.name} x {self.quantity}"



class DailySummary(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.IntegerField(default=0)

    def __str__(self):
        return f"Summary - {self.date}"
