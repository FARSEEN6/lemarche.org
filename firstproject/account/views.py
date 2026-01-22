import razorpay
import json

from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt

from .models import Cart
from product.models import Product


# 🔐 LOGIN
def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Login successful")
            return redirect("home")
        else:
            messages.error(request, "Invalid credentials")

    return render(request, "login.html")


# 📝 REGISTER
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "All fields required")
            return render(request, "register.html")

        try:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Registration successful")
            return redirect("login")
        except IntegrityError:
            messages.error(request, "Username already exists")

    return render(request, "register.html")


# 🚪 LOGOUT
def logout_view(request):
    logout(request)
    return redirect("login")


# 👤 PROFILE
@login_required
def profile_view(request):
    return render(request, "profile.html")


# 🛒 CART
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("product")
    total = sum(item.line_total for item in cart_items)

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect("cart")


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if request.method == "POST":
        qty = int(request.POST.get("quantity", 1))
        cart_item.quantity = max(qty, 1)
        cart_item.save()

    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)
    cart_item.delete()
    return redirect("cart")


# 💳 REAL RAZORPAY CHECKOUT (PAGE NAME UNCHANGED)
@login_required
def dummy_checkout(request):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.line_total for item in cart_items)

    if total == 0:
        messages.error(request, "Cart is empty")
        return redirect("cart")

    client = razorpay.Client(
        auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
    )

    order = client.order.create({
        "amount": int(total * 100),  # paise
        "currency": "INR",
        "payment_capture": 1
    })

    context = {
        "total": total,
        "razorpay_key": settings.RAZORPAY_KEY_ID,
        "razorpay_order_id": order["id"],
        "razorpay_amount": int(total * 100)
    }

    return render(request, "dummy_checkout.html", context)


# ✅ PAYMENT SUCCESS HANDLER
@csrf_exempt
def razorpay_success(request):
    if request.method == "POST":
        data = json.loads(request.body)

        # OPTIONAL: signature verification here

        Cart.objects.filter(user=request.user).delete()
        return redirect("dummy_payment_success")


@login_required
def dummy_payment_success(request):
    return render(request, "dummy_success.html")
