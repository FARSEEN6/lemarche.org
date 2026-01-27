
from django.urls import path
from . import views

urlpatterns = [

    # AUTH
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile_view, name="profile"),

    # CART
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:product_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/buy/<int:product_id>/", views.buy_now, name="buy_now"),
    path("cart/update/<int:item_id>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:item_id>/", views.remove_from_cart, name="remove_from_cart"),

    # PAYMENT
    path("checkout/dummy/", views.dummy_checkout, name="dummy_checkout"),
    path("razorpay/success/", views.razorpay_success, name="razorpay_success"),
    path("payment/success/", views.dummy_payment_success, name="dummy_payment_success"),

    # WISHLIST
    path("wishlist/", views.wishlist_view, name="wishlist"),
    path("wishlist/toggle/<int:product_id>/", views.toggle_wishlist, name="toggle_wishlist"),

    # CHECKOUT FLOW
    path("checkout/address/", views.checkout_address, name="checkout_address"),
    path("checkout/payment/", views.checkout_payment, name="checkout_payment"),
    path("gpay/scan/", views.gpay_scan, name="gpay_scan"),

    # ADMIN
    path("dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("order/edit/<int:order_id>/", views.edit_order, name="edit_order"),
    path("order/update-items/<int:order_id>/", views.update_order_items, name="update_order_items"),
    path("order/delete/<int:order_id>/", views.delete_order, name="delete_order"),
]
