# account/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.admin.views.decorators import staff_member_required  # ⬅ NEW

from .models import Cart
from product.models import Product
from product.form import productForm  # ⬅ adjust to product.forms if needed


# 🔐 LOGIN VIEW
def login_view(request):
    # already logged in user → go to profile
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful.")
            return redirect("home")  # make sure URL name is 'profile'
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, "login.html")


# 📝 REGISTER VIEW
def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "").strip()

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return render(request, "register.html")

        if len(password) < 4:
            messages.error(request, "Password must be at least 4 characters long.")
            return render(request, "register.html")

        try:
            User.objects.create_user(username=username, password=password)
            messages.success(request, "Registration successful. You can now log in.")
            return redirect("login")
        except IntegrityError:
            messages.error(request, "Username already exists.")
            return render(request, "register.html")

    return render(request, "register.html")


# 👤 PROFILE VIEW
@login_required
def profile_view(request):
    return render(request, "profile.html")


# 🚪 LOGOUT VIEW
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("login")


# 🛒 CART VIEWS
@login_required
def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user).select_related("product")
    total = sum(item.line_total for item in cart_items)  # assumes Cart has line_total property

    return render(request, "cart.html", {
        "cart_items": cart_items,
        "total": total,
    })


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Item added to cart.")
    return redirect("cart")


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if request.method == "POST":
        qty = request.POST.get("quantity", "1")
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 1

        if qty < 1:
            qty = 1

        cart_item.quantity = qty
        cart_item.save()
        messages.success(request, "Cart updated.")

    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if request.method == "POST":
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect("cart")


# 💳 DUMMY CHECKOUT
@login_required
def dummy_checkout(request):
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method == 'upi':
            upi_id = request.POST.get('upi_id')
            txn_id = request.POST.get('upi_txn_id')
            # handle UPI details here if needed

        elif payment_method == 'card':
            card_number = request.POST.get('card_number')
            name_on_card = request.POST.get('name_on_card')
            # handle card details here if needed

        return redirect('dummy_payment_success')

    return render(request, "dummy_checkout.html")


@login_required
def dummy_payment_success(request):
    return render(request, "dummy_success.html")


# # 🧑‍💻 ADD PRODUCTS (ADMIN / STAFF ONLY)
# @staff_member_required
# def add_products(request):
#     if request.method == 'POST':
#         form = productForm(request.POST, request.FILES)
#         if form.is_valid():
#             form.save()
#             messages.success(request, "Product added successfully!")
#             return redirect('product')
#         else:
#             messages.error(request, "Please correct the errors below.")
#     else:
#         form = productForm()

#     return render(request, 'add_product.html', {'form': form})



@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if request.method == "POST":
        qty = request.POST.get("quantity", "1")
        try:
            qty = int(qty)
        except (TypeError, ValueError):
            qty = 1

        if qty < 1:
            qty = 1

        cart_item.quantity = qty
        cart_item.save()
        messages.success(request, "Cart updated.")

    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(Cart, id=item_id, user=request.user)

    if request.method == "POST":
        cart_item.delete()
        messages.success(request, "Item removed from cart.")

    return redirect("cart")
