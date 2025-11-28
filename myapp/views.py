from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta

from .models import Product, StockHistory, Sale, DailySummary
from .forms import ProductForm, StockForm, SaleForm

@login_required
def dashboard(request):
    total_products = Product.objects.count()
    today = date.today()
    todays_sales = Sale.objects.filter(date_sold__date=today).count()
    low_stock_count = Product.objects.filter(quantity__lte=5).count()

    near_expiry_limit = today + timedelta(days=7)
    expired_count = Product.objects.filter(expiry_date__lt=today).count()
    near_expiry_count = Product.objects.filter(expiry_date__range=[today, near_expiry_limit]).count()
    expired_total = expired_count + near_expiry_count

    context = {
        'total_products': total_products,
        'todays_sales': todays_sales,
        'low_stock_count': low_stock_count,
        'expired_count': expired_total,
    }
    return render(request, 'dashboard.html', context)

@login_required
def product_list(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'products.html', {'products': products})

@login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            # quantity starts at 0 until stock added
            p.quantity = p.quantity or 0
            p.save()
            messages.success(request, 'Product registered successfully.')
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})

@login_required
def add_stock(request):
    """
    Add stock: creates StockHistory and increments Product.quantity
    """
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            product = stock.product
            qty = stock.quantity_added
            # update product quantity
            product.quantity += qty
            # if expiry provided on stock batch, optionally set product expiry (business rule)
            # we do not overwrite product.expiry_date unless provided
            if stock.expiry_date:
                product.expiry_date = stock.expiry_date
            product.save()
            stock.save()
            messages.success(request, f'Stock added: {product.name} +{qty}')
            return redirect('product_list')
    else:
        form = StockForm()
    return render(request, 'add_stock.html', {'form': form})

@login_required
def add_sale(request):
    """
    Add sale: ensures there is enough stock, deducts product.quantity, records Sale.
    """
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            product = sale.product
            qty = sale.quantity_sold

            if qty <= 0:
                messages.error(request, 'Quantity must be at least 1.')
                return redirect('add_sale')

            if product.quantity < qty:
                messages.error(request, f'Not enough stock for {product.name}. Available: {product.quantity}')
                return redirect('add_sale')

            # compute pricing
            sale.price_each = product.selling_price
            sale.total_price = sale.price_each * qty

            # deduct stock
            product.quantity -= qty
            product.save()

            sale.save()

            # optionally update daily summary (simple)
            ds, created = DailySummary.objects.get_or_create(date=date.today())
            ds.total_sales += sale.total_price
            ds.total_items_sold += qty
            ds.save()

            messages.success(request, f'Sale recorded: {product.name} x{qty}')
            return redirect('dashboard')
    else:
        form = SaleForm()
    return render(request, 'add_sale.html', {'form': form})

@login_required
def sales_list(request):
    sales = Sale.objects.select_related('product').order_by('-date_sold')[:200]
    return render(request, 'sales.html', {'sales': sales})

@login_required
def expired_list(request):
    today = date.today()
    near_expiry_limit = today + timedelta(days=7)
    expired = Product.objects.filter(expiry_date__lt=today)
    near_expiry = Product.objects.filter(expiry_date__range=[today, near_expiry_limit])
    return render(request, 'expired.html', {'expired': expired, 'near_expiry': near_expiry})
