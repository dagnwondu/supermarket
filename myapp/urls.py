from django.urls import path
from . import views
urlpatterns = [
    path('', views.login, name='login'),
    path('products/', views.product_list, name='products'),
    path('add-product/', views.add_product, name='add_product'),
    path('add-stock/', views.add_stock, name='add_stock'),
    path('add-sale/', views.add_sale, name='add_sale'),
    path('cashier_add_sale/', views.cashier_add_sale, name='cashier_add_sale'),
    path('sales/', views.sales, name='sales'),
    path('cashier_sales/', views.cashier_sales, name='cashier_sales'),
    path('api/products/search/', views.product_search, name='product_search'),  # <-- this is needed
    path('expired/', views.expired_list, name='expired_list'),
    path('near_expiry_stocks/', views.near_expiry_stocks, name='near_expiry_stocks'),
    path('stock_deatil/<int:stock_id>/', views.stock_deatil, name='stock_deatil'),    
    path('delete_stock/<int:stock_id>/', views.delete_stock, name='delete_stock'),    
    path('add-category/', views.add_category, name='add_category'),
    path('products/edit/<int:product_id>/', views.edit_product, name='edit_product'),
    path('products/<int:product_id>/batches/', views.product_batches, name='product_batches'),
    path('sales/<int:sale_id>/', views.sale_detail, name='sale_detail'),
    path('manage_users/', views.manage_users, name = 'manage_users'),   
    path('delete_user/<int:user_id>/', views.delete_user, name = 'delete_user'),   
    path('update_user/<int:user_id>/', views.update_user, name = 'update_user'),   
    path('update_user_submit/<int:user_id>/', views.update_user_submit, name = 'update_user_submit'),   
    path('change_password/<int:user_id>/', views.change_password, name = 'change_password'),   

]
