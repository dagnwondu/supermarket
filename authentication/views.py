from django.shortcuts import render, redirect,get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from datetime import date
from django.views.generic import ListView
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from . models import CustomUser, Company
from django.shortcuts import render,redirect, reverse
from django.core.paginator import Paginator
from myapp.models import Product, Sale, SaleItem, Stock
from . forms import UserForm, UserUpdateForm
from datetime import date, timedelta
from django.db.models import Sum
from django.utils.timezone import now
today = now().date()
from django.db.models import Sum
from django.utils.timezone import now



# Create your views here.
# Identify users role and redirect to their view
def home(request):
    try:
        # Get the current user's user_type
        user = CustomUser.objects.get(id=request.user.id)
        user_role = user.user_type.lower()  # e.g., "admin", "doctor", etc.

        # Redirect based on user role
        if user_role == 'admin':
            return redirect('admin_view')
        elif user_role == 'cashier':
            return redirect('cashier_view')
    except CustomUser.DoesNotExist:
        messages.error(request, 'User not found.')
        return redirect('/')

    # If no matching role is found
    messages.error(request, 'Unauthorized access.')
    return redirect('/')

# Login Page
def loginPage(request):
    return redirect(reverse('login'))  # Assuming 'login' is the name of the login URL
# Checking if the user is an admin
def is_admin(user):
    return user.user_type == 'admin'
def is_cashier(user):
    return user.user_type == 'cashier'


# Admin View
@login_required(login_url='/accounts/login')
@user_passes_test(is_admin)
def admin_view(request):
    today = now().date()
    # Aggregate total quantity and total revenue from SaleItem
    today_sales = SaleItem.objects.filter(sale__created_at__date=today).aggregate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    )
    low_stock_count = sum(1 for p in Product.objects.all() if p.low_stock)
    products_count = Product.objects.all().count()
    today = date.today()
    near_expiry_limit = today + timedelta(days=90)

    expired_count = Stock.objects.filter(expiry_date__lt=today).count()
    near_expiry_count = Stock.objects.filter(expiry_date__range=[today, near_expiry_limit]).count()
    near_expiry = Stock.objects.filter(expiry_date__range=[today, near_expiry_limit])
    context = {
        "expired_count":expired_count,
        'near_expiry':near_expiry,
        'near_expiry_count':near_expiry_count,
        "low_stock_count":low_stock_count,
        'products': products_count,
        'today_total_quantity': today_sales['total_quantity'] or 0,
        'today_sales_birr': today_sales['total_revenue'] or 0,
    }

    return render(request, 'admin_page.html', context)

# Admin View
@login_required(login_url='/accounts/login')
@user_passes_test(is_cashier)
def cashier_view(request):
    today = now().date()
    # Aggregate total quantity and total revenue from SaleItem
    today_sales = SaleItem.objects.filter(sale__created_at__date=today).aggregate(
        total_quantity=Sum('quantity'),
        total_revenue=Sum('total_price')
    )
    low_stock_count = sum(1 for p in Product.objects.all() if p.low_stock)
    products_count = Product.objects.all().count()
    today = date.today()
    near_expiry_limit = today + timedelta(days=90)

    expired_count = Stock.objects.filter(expiry_date__lt=today).count()
    near_expiry_count = Stock.objects.filter(expiry_date__range=[today, near_expiry_limit]).count()
    near_expiry = Stock.objects.filter(expiry_date__range=[today, near_expiry_limit])
    context = {
        "expired_count":expired_count,
        'near_expiry':near_expiry,
        'near_expiry_count':near_expiry_count,
        "low_stock_count":low_stock_count,
        'products': products_count,
        'today_total_quantity': today_sales['total_quantity'] or 0,
        'today_sales_birr': today_sales['total_revenue'] or 0,
    }

    return render(request, 'cashier_page/cashier_page.html', context)


@login_required
def password_change(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    if request.method == "POST":
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password == confirm_password:
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password changed successfully!")
        else:
            messages.error(request, "Passwords do not match.")

    return redirect('manage_users')  # Adjust to your URL name
