from django.urls import path
from .views import (
    Home,
    product,
    detail_product,
    delete_product,
    add_products,
    edit_products,
    toggle_stock,
    rate_product,
)

urlpatterns = [
    path('', Home, name='home'),
    path('product/', product, name='product'),

    path('product/add/', add_products, name='add_products'),
    path('product/<int:id>/', detail_product, name='detail_page'),
    path('product/<int:id>/edit/', edit_products, name='edit_products'),
    path('product/<int:id>/delete/', delete_product, name='delete_product'),

    # ⭐ STAR RATING
    path('product/<int:product_id>/rate/', rate_product, name='rate_product'),

    path('product/<int:id>/toggle-stock/', toggle_stock, name='toggle_stock'),
]
