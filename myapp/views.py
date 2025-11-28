# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib import messages
# from django.urls import reverse
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.core.paginator import Paginator
# from django.contrib.auth.decorators import login_required
# from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from .models import Product, Stock, Sale, DailySummary
from .forms import ProductForm, StockForm, SaleForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from .models import Product, Stock, Sale
from django.db.models import Sum
from django.db.models import Q
from .models import Category, Product, Stock

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

    # ----- PAGINATION -----
    paginator = Paginator(products, 10)  # 10 products per page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    # ------------------------

    return render(request, 'products.html', {'page_obj': page_obj})

# from django.shortcuts import render, redirect
# from .models import Category
# from django.contrib import messages
# from django.contrib.auth.decorators import login_required

@login_required
def add_category(request):
    if request.method == "POST":
        name = request.POST['name']
        description = request.POST.get('description', '')
        if Category.objects.filter(name=name).exists():
            messages.error(request, "Category already exists.")
        else:
            Category.objects.create(name=name, description=description)
            messages.success(request, f"Category '{name}' added successfully.")
        return redirect('add_category')

    categories = Category.objects.all()
    return render(request, 'add_category.html', {'categories': categories})


# @login_required
# def add_stock(request):
#     """
#     Add stock: creates Stock and increments Product.quantity
#     """
#     if request.method == 'POST':
#         form = StockForm(request.POST)
#         if form.is_valid():
#             stock = form.save(commit=False)
#             product = stock.product
#             qty = stock.quantity_added
#             # update product quantity
#             product.quantity += qty
#             # if expiry provided on stock batch, optionally set product expiry (business rule)
#             # we do not overwrite product.expiry_date unless provided
#             if stock.expiry_date:
#                 product.expiry_date = stock.expiry_date
#             product.save()
#             stock.save()
#             messages.success(request, f'Stock added: {product.name} +{qty}')
#             return redirect('product_list')
#     else:
#         form = StockForm()
#     return render(request, 'add_stock.html', {'form': form})

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



def product_search(request):
    q = request.GET.get("q", "")

    products = Product.objects.filter(
        Q(name__icontains=q) |
        Q(barcode__icontains=q) |
        Q(category__name__icontains=q)
    )

    data = []
    for p in products:
        data.append({
            "id": p.id,
            "name": p.name,
            "barcode": p.barcode,
            "category": p.category.name if p.category else "",
            "selling_price": p.selling_price,
            "quantity": p.total_stock,
        })

    return JsonResponse(data, safe=False)

# ----------------------
# Category Views
# ----------------------


# ----------------------
# Product Views
# ----------------------
login_required
def add_product(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Product added successfully!")
            return redirect('add_product')
    else:
        form = ProductForm()
    return render(request, 'add_product.html', {'form': form})
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save()
            messages.success(request, f"Stock added: {stock.quantity} units of {stock.product.name}")
            return redirect('add_stock')
    else:
        form = StockForm()
    return render(request, 'add_stock.html', {'form': form})
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form})
def product_batches(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    batches = Stock.objects.filter(product=product).order_by('-added_at')

    return render(request, 'product_batches.html', {
        'product': product,
        'batches': batches
    })
def sales(request):

    sales = Sale.objects.select_related("product").order_by("-created_at")

    # --- Filters ---
    search = request.GET.get("search")
    product_id = request.GET.get("product")
    category_id = request.GET.get("category")
    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    price_min = request.GET.get("price_min")
    price_max = request.GET.get("price_max")

    if search:
        sales = sales.filter(product__name__icontains=search)

    if product_id:
        sales = sales.filter(product_id=product_id)

    if category_id:
        sales = sales.filter(product__category_id=category_id)

    if date_from:
        sales = sales.filter(created_at__date__gte=date_from)

    if date_to:
        sales = sales.filter(created_at__date__lte=date_to)

    if price_min:
        sales = sales.filter(total_price__gte=price_min)

    if price_max:
        sales = sales.filter(total_price__lte=price_max)

    return render(request, "sales.html", {
        "sales": sales,
        "products": Product.objects.all(),
        "categories": Category.objects.all(),
        "values": request.GET
    })

def add_sale(request):
    if request.method == "POST":
        product_id = request.POST.get("product_id")
        quantity = int(request.POST.get("quantity"))

        product = get_object_or_404(Product, id=product_id)
        # total_available = product.stock_set.aggregate(total=Sum('quantity'))['total'] or 0
        total_available = product.batches.aggregate(total=Sum('quantity'))['total'] or 0

        if quantity > total_available:
            messages.error(request, "Quantity exceeds available stock!")
            return redirect('add_sale')

        # Deduct stock using FIFO
        remaining = quantity
        batches = Stock.objects.filter(product=product, quantity__gt=0).order_by('added_at')

        with transaction.atomic():
            for batch in batches:
                if remaining == 0:
                    break
                if batch.quantity >= remaining:
                    batch.quantity -= remaining
                    batch.save()
                    remaining = 0
                else:
                    remaining -= batch.quantity
                    batch.quantity = 0
                    batch.save()

            Sale.objects.create(
                product=product,
                quantity=quantity,
                total_price=product.selling_price * quantity
            )

        messages.success(request, "Sale recorded successfully!")
        return redirect('add_sale')

    return render(request, "add_sale.html")
