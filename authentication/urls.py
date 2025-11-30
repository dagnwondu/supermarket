from django.urls import path
from . import views
urlpatterns = [
    # Authentication urls
    path('', views.home, name = 'home'),   
    # Cashier urls
    # path('cashier_view/', views.cashier_view, name = 'cashier_view'),   
    # Admin urls
    path('admin_view/', views.admin_view, name = 'admin_view'),   
]
