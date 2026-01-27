
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
from django.utils import timezone
from django.db.models import Sum

from .models import Cart, Wishlist, Order, OrderItem
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

    messages.success(request, "Added to cart")
    return redirect(request.META.get("HTTP_REFERER", "product"))


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


@login_required
def buy_now(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    # Add to cart (or get existing)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    # If not created, increment? Optional. For "Buy Now" usually we just ensure it's in cart.
    # Let's say we ensure at least 1 is in cart.
    if not created:
         # Optionally update quantity or just leave it. 
         # For a direct "Buy Now", let's leave it as is, or maybe ensure session knows this is immediate buy? 
         # For simplicity: Just ensure it's in cart and go to checkout.
         pass
    
    return redirect("checkout_address")



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


# ❤️ WISHLIST
@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related("product")
    return render(request, "wishlist.html", {"wishlist_items": wishlist_items})


@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    w_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if not created:
        w_item.delete()
        messages.info(request, "Removed from Wishlist")
    else:
        messages.success(request, "Added to Wishlist")

    # Redirect back to previous page
    return redirect(request.META.get("HTTP_REFERER", "home"))


# 🚚 CHECKOUT: ADDRESS
@login_required
def checkout_address(request):
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        messages.error(request, "Your cart is empty")
        return redirect("cart")

    if request.method == "POST":
        # Save address to session to pass to payment step
        request.session['checkout_address'] = {
            'customer_name': request.POST.get('customer_name'),
            'address_line1': request.POST.get('address_line1'),
            'address_line2': request.POST.get('address_line2'),
            'city': request.POST.get('city'),
            'state': request.POST.get('state'),
            'pincode': request.POST.get('pincode'),
            'phone_number': request.POST.get('phone_number'),
        }
        return redirect("checkout_payment")

    return render(request, "address_form.html")


# 💳 CHECKOUT: PAYMENT
@login_required
def checkout_payment(request):
    address_data = request.session.get('checkout_address')
    if not address_data:
        return redirect("checkout_address")
    
    cart_items = Cart.objects.filter(user=request.user)
    if not cart_items.exists():
        return redirect("cart")
        
    total = sum(item.line_total for item in cart_items)

    if request.method == "POST":
        method = request.POST.get("payment_method")
        
        # 1. CASH ON DELIVERY
        if method == "COD":
            return create_order(request, address_data, "COD", "Pending")

        # 2. GOOGLE PAY (UPI)
        elif method == "GPAY":
            return redirect("gpay_scan")

        # 3. NETBANKING -> Redirect to dummy Razorpay
        elif method == "NETBANKING":
             return redirect("dummy_checkout")
    
    return render(request, "payment_select.html", {"total": total})


#  helper to create order
def create_order(request, address_data, payment_method, status):
    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.line_total for item in cart_items)

    order = Order.objects.create(
        user=request.user,
        customer_name=address_data['customer_name'],
        address_line1=address_data['address_line1'],
        address_line2=address_data.get('address_line2', ''),
        city=address_data['city'],
        state=address_data['state'],
        pincode=address_data['pincode'],
        phone_number=address_data['phone_number'],
        payment_method=payment_method,
        status=status,
        total_amount=total
    )

    # Move items to OrderItem
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.p_price
        )
    
    # Clear Cart
    cart_items.delete()
    
    # Clear session
    if 'checkout_address' in request.session:
        del request.session['checkout_address']
        
    return redirect("dummy_payment_success")


# 🔵 GPAY SCAN VIEW
@login_required
def gpay_scan(request):
    address_data = request.session.get('checkout_address')
    if not address_data:
        return redirect("checkout_address")

    cart_items = Cart.objects.filter(user=request.user)
    total = sum(item.line_total for item in cart_items)

    if request.method == "POST":
         # User claims they paid. Create order.
         return create_order(request, address_data, "GPAY", "Paid")
    
    return render(request, "gpay_scan.html", {"total": total})


# 👮 ADMIN DASHBOARD
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        messages.error(request, "Access Denied. Admins only.")
        return redirect("home")

    # Stats
    total_orders = Order.objects.count()
    paid_orders = Order.objects.filter(status='Paid').count()
    
    today_sales = Order.objects.filter(
        status='Paid', 
        created_at__date=timezone.now().date()
    ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    stats = {
        'total_orders': total_orders,
        'paid_orders': paid_orders,
        'today_sales': today_sales
    }

    # Order retrieval needed for list
    orders = Order.objects.select_related("user").prefetch_related("items__product").order_by("-created_at")

    # Search functionality
    query = request.GET.get('q')
    if query:
        orders = orders.filter(
            id__icontains=query
        ) | orders.filter(
            customer_name__icontains=query
        ) | orders.filter(
            phone_number__icontains=query
        )

    return render(request, "admin_dashboard.html", {
        "orders": orders,
        "stats": stats,
        "query": query or ""
    })

# ✏️ EDIT ORDER (Admin)
@login_required
def edit_order(request, order_id):
    if not request.user.is_staff:
         messages.error(request, "Access Denied.")
         return redirect("home")
         
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        order.customer_name = request.POST.get("customer_name")
        order.phone_number = request.POST.get("phone_number")
        order.address_line1 = request.POST.get("address_line1")
        order.address_line2 = request.POST.get("address_line2")
        order.city = request.POST.get("city")
        order.state = request.POST.get("state")
        order.pincode = request.POST.get("pincode")
        
        order.payment_method = request.POST.get("payment_method")
        order.status = request.POST.get("status")
        
        order.save()
        messages.success(request, "Order updated successfully")
        return redirect("admin_dashboard")
        
    return render(request, "edit_dashbord.html", {"order": order})


# 🔄 UPDATE ORDER ITEMS (Admin)
@login_required
def update_order_items(request, order_id):
    if not request.user.is_staff:
        return redirect("home")
        
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("qty_"):
                item_id = key.split("_")[1]
                qty = int(value)
                
                try:
                    item = OrderItem.objects.get(id=item_id, order=order)
                    if qty > 0:
                        item.quantity = qty
                        item.save()
                    else:
                        item.delete()
                except OrderItem.DoesNotExist:
                    pass
        
        # Recalculate order total
        new_total = sum(item.quantity * item.price for item in order.items.all())
        order.total_amount = new_total
        order.save()
        
        messages.success(request, "Order items updated")
        return redirect("edit_order", order_id=order.id)
    
    return redirect("admin_dashboard")


# 🗑️ DELETE ORDER (Admin)
@login_required
def delete_order(request, order_id):
    if not request.user.is_staff:
        return redirect("home")
        
    order = get_object_or_404(Order, id=order_id)
    order.delete()
    messages.success(request, "Order deleted")
    return redirect("admin_dashboard")
