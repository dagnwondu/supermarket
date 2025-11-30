from django.db import models
from datetime import date
from django.db.models import Sum
from datetime import date, timedelta
from django.conf import settings

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
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    low_stock_threshold = models.PositiveIntegerField(default=10)  # NEW FIELD
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def total_stock(self):
        return self.batches.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def low_stock(self):
        """Returns True if total stock is below threshold."""
        return self.total_stock <= self.low_stock_threshold


class Stock(models.Model):
    product = models.ForeignKey(Product,related_name="batches", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    buying_price = models.DecimalField(max_digits=10, decimal_places=2)
    batch_number = models.CharField(max_length=100, blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} units"
    @property
    def total_stock(self):
        return self.batches.aggregate(total=models.Sum('quantity'))['total'] or 0

    @property
    def low_stock(self):
        return self.total_stock <= self.low_stock_threshold

    @property
    def has_expired(self):
        """Return True if any related batch is expired."""
        # batches is the related_name from Stock/Batch foreign key
        return any(getattr(batch, 'expiry_date', None) and batch.expiry_date < date.today()
                   for batch in self.batches.all())

    @property
    def has_near_expiry(self):
        """Return True if any related batch expires within next 90 days (including today)."""
        warn_until = date.today() + timedelta(days=90)
        return any(getattr(batch, 'expiry_date', None) and date.today() <= batch.expiry_date <= warn_until
                   for batch in self.batches.all())


class DailySummary(models.Model):
    date = models.DateField(unique=True)
    total_sales = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_items_sold = models.IntegerField(default=0)

    def __str__(self):
        return f"Summary - {self.date}"
class Sale(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # total for all items
    sold_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sales', null=True, blank=True
    )
    def __str__(self):
        return f"Sale #{self.id} - {self.created_at.date()}"

    @property
    def total_quantity(self):
        return self.items.aggregate(total=Sum('quantity'))['total'] or 0


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name="items", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)  # price per unit
    total_price = models.DecimalField(max_digits=12, decimal_places=2)  # quantity * selling_price

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

    def save(self, *args, **kwargs):
        self.total_price = self.quantity * self.selling_price
        super().save(*args, **kwargs)
