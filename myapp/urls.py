from django.urls import path
from . import views
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='products'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('add-sale/', views.add_sale, name='add_sale'),
    path('sales/', views.sales, name='sales'),
    path('api/products/search/', views.product_search, name='product_search'),  # <-- this is needed
    path('expired/', views.expired_list, name='expired_list'),
    # path('products/search/', views.product_search, name='product_search'),
    path('add-category/', views.add_category, name='add_category'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/batches/', views.product_batches, name='product_batches'),
    path('sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),

]
