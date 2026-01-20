from django.urls import path
from django.contrib import admin
from django.urls import include
from .views import (
    Home,
    product,
    detail_product,
    delete_product,
    add_products,
    edit_products,
)


urlpatterns = [
    path('', Home, name='home'),
    path('product/', product, name='product'),
    path('admin/', admin.site.urls),

    # include account app at root
    path('', include('account.urls')),

    path('product/add/', add_products, name='add_products'),
    path('product/<int:id>/', detail_product, name='detail_page'),
    path('product/<int:id>/edit/', edit_products, name='edit_products'),
    path('product/<int:id>/delete/', delete_product, name='delete_product'),


    
]
