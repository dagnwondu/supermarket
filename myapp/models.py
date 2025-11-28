from django.db import models
from datetime import date
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
class Product(models.Model):
    name = models.CharField(max_length=200)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    barcode = models.CharField(max_length=100, blank=True, null=True)

    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)

    quantity = models.IntegerField(default=0)  # current stock

    expiry_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        if self.expiry_date:
            return self.expiry_date < date.today()
        return False

    def __str__(self):
        return self.name


class StockHistory(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='stock_entries')
    quantity_added = models.IntegerField()
    date_added = models.DateTimeField(auto_now_add=True)

    # optional — useful if different stock batches have different expiry dates
    expiry_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.product.name} +{self.quantity_added}"


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity_sold = models.IntegerField()

    price_each = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    date_sold = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Deduct stock when sale is created
        if not self.id:  # prevent double deduction on update
            self.product.quantity -= self.quantity_sold
            self.product.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Sale - {self.product.name} ({self.quantity_sold})"


class DailySummary(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.IntegerField(default=0)

    def __str__(self):
        return f"Summary - {self.date}"
