from django.urls import path
from . import views

urlpatterns = [

    # 🔐 AUTH ROUTES
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # 🛒 CART ROUTES
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # 💳 PAYMENT / CHECKOUT (DUMMY)
    path('checkout/dummy/', views.dummy_checkout, name='dummy_checkout'),
    path('payment/success/', views.dummy_payment_success, name='dummy_payment_success'),
]
