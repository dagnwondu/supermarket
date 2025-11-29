from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from django.http import JsonResponse
from .models import Product, Stock, Sale, DailySummary, SaleItem,Category
from .forms import ProductForm, StockForm, SaleForm
from django.db.models import Sum, Prefetch, Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
@login_required
def dashboard(request):
    total_products = Product.objects.count()
    today = date.today()
    todays_sales = Sale.objects.filter(created_at__date=today).count()
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
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category')
    filter_type = request.GET.get('filter')  # low_stock | near_expiry

    products = Product.objects.all().order_by('name')

    # -------------------------------------
    # SEARCH
    # -------------------------------------
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(barcode__icontains=search)
        )

    # -------------------------------------
    # CATEGORY FILTER
    # -------------------------------------
    if category:
        products = products.filter(category_id=category)

    # -------------------------------------
    # LOW STOCK FILTER
    # -------------------------------------
    if filter_type == "low_stock":
        products = [p for p in products if p.low_stock]

    # -------------------------------------
    # NEAR EXPIRY FILTER (within 90 days)
    # -------------------------------------
    elif filter_type == "near_expiry":
        threshold_date = date.today() + timedelta(days=90)

        filtered = []
        for product in products:
            for batch in product.batches.all():
                if batch.expiry_date and batch.expiry_date <= threshold_date:
                    filtered.append(product)
                    break
        products = filtered

    # -------------------------------------
    # PAGINATION
    # -------------------------------------
    paginator = Paginator(products, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()

    context = {
        'page_obj': page_obj,
        'categories': categories,
        'values': request.GET,
        'filter': filter_type,
    }

    return render(request, 'products.html', context)
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
login_required
def add_stock(request):
    """
    Add new stock batch for a product.
    Updates product selling price if changed.
    """
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        buying_price = request.POST.get('buying_price')
        selling_price = request.POST.get('selling_price')
        expiry_date = request.POST.get('expiry_date') or None  # optional

        # Basic validation
        if not product_id or not quantity or not buying_price or not selling_price:
            messages.error(request, "Please fill in all required fields.")
            return redirect('add_stock')

        try:
            quantity = int(quantity)
            buying_price = float(buying_price)
            selling_price = float(selling_price)
        except ValueError:
            messages.error(request, "Invalid number entered.")
            return redirect('add_stock')

        if quantity <= 0 or buying_price <= 0 or selling_price <= 0:
            messages.error(request, "Quantity and prices must be positive.")
            return redirect('add_stock')

        # Get product
        product = get_object_or_404(Product, id=product_id)

        # Update product selling price if changed
        if product.selling_price != selling_price:
            product.selling_price = selling_price
            product.save()
        import datetime

        batch_number = f"{product.id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

        # Create stock batch
        stock = Stock.objects.create(
            product=product,
            quantity=quantity,
            buying_price=buying_price,
            batch_number=batch_number,  # optional: can auto-generate
            expiry_date=expiry_date
        )

        messages.success(request, f"Stock added: {stock.quantity} units of {product.name}")
        return redirect('add_stock')
    return render(request, 'add_stock.html')
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
@login_required
def add_sale(request):
    """
    Multi-item sale:
    - Validate stock for each product
    - Deduct stock using FIFO
    - Create Sale and SaleItem entries
    - Update daily summary
    """
    if request.method == 'POST':
        product_ids = request.POST.getlist('product_id[]')
        quantities = request.POST.getlist('quantity[]')

        if not product_ids or not quantities:
            messages.error(request, "No products selected.")
            return redirect('add_sale')

        # Convert quantities to integers
        try:
            quantities = [int(q) for q in quantities]
        except (ValueError, TypeError):
            messages.error(request, "Invalid quantity entered.")
            return redirect('add_sale')

        # Validate stock for all selected products
        products = Product.objects.filter(id__in=product_ids)
        product_map = {str(p.id): p for p in products}
        stock_errors = []

        for pid, qty in zip(product_ids, quantities):
            product = product_map.get(pid)
            if not product:
                stock_errors.append(f"Product with ID {pid} not found.")
            elif qty <= 0:
                stock_errors.append(f"Quantity for {product.name} must be at least 1.")
            elif product.total_stock < qty:
                stock_errors.append(f"Not enough stock for {product.name}. Available: {product.total_stock}")

        if stock_errors:
            messages.error(request, " | ".join(stock_errors))
            return redirect('add_sale')

        # All validations passed, save sale
        with transaction.atomic():
            sale = Sale.objects.create(total_price=0)
            grand_total = 0

            for pid, qty in zip(product_ids, quantities):
                product = product_map[pid]

                # Deduct stock using FIFO
                remaining = qty
                batches = product.batches.filter(quantity__gt=0).order_by('added_at')
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

                # Compute item total
                total_price = qty * product.selling_price
                grand_total += total_price

                # Create SaleItem
                SaleItem.objects.create(
                    sale=sale,
                    product=product,
                    quantity=qty,
                    selling_price=product.selling_price,
                    total_price=total_price
                )

            # Update Sale grand total
            sale.total_price = grand_total
            sale.save()

            # Update daily summary
            ds, created = DailySummary.objects.get_or_create(date=date.today())
            ds.total_sales += grand_total
            ds.total_items_sold += sum(quantities)
            ds.save()

            messages.success(request, f"Sale recorded successfully! Grand Total: {grand_total:.2f} Birr")
            return redirect('dashboard')

    return render(request, 'add_sale.html')
def sales(request):
    # GET filter values
    search = request.GET.get('search', '').strip()
    category = request.GET.get('category')
    product_id = request.GET.get('product')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    price_min = request.GET.get('price_min')
    price_max = request.GET.get('price_max')

    # Prefetch SaleItems with Product
    sale_items_qs = SaleItem.objects.select_related('product')
    sales = Sale.objects.prefetch_related(
        Prefetch('items', queryset=sale_items_qs, to_attr='sale_items')
    ).order_by('-created_at')

    # FILTERS
    if search:
        sales = sales.filter(items__product__name__icontains=search).distinct()
    if category:
        sales = sales.filter(items__product__category_id=category).distinct()
    if product_id:
        sales = sales.filter(items__product_id=product_id).distinct()
    if date_from:
        sales = sales.filter(created_at__date__gte=date_from)
    if date_to:
        sales = sales.filter(created_at__date__lte=date_to)

    # Compute totals per sale for display
    for sale in sales:
        sale.total_items = sum(item.quantity for item in sale.sale_items)
        sale.total_price = sum(item.total_price for item in sale.sale_items)
        sale.product_names = ", ".join([item.product.name for item in sale.sale_items])

    # PAGINATION
    paginator = Paginator(sales, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'sales': page_obj,
        'page_obj': page_obj,
        'categories': Category.objects.all(),
        'products': Product.objects.all(),
        'values': request.GET,
    }
    return render(request, 'sales.html', context)
def sale_detail(request, sale_id):
    sale = get_object_or_404(Sale, id=sale_id)
    sale_items = sale.items.select_related('product')

    grand_total = sale_items.aggregate(total=Sum('total_price'))['total'] or 0

    context = {
        'sale': sale,
        'sale_items': sale_items,
        'grand_total': grand_total,
    }
    return render(request, 'sale_detail.html', context)
