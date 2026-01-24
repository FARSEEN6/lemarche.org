from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, Count

from .models import Product, ProductRating
from .forms import productForm


def Home(request):
    # Show last 4 added products (Latest Arrivals)
    products = Product.objects.all().order_by('-id')[:4]
    return render(request, "home.html", {"products": products})


def product(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.all()

    if q:
        products = products.filter(
            Q(p_name__icontains=q) |
            Q(p_category__icontains=q) |
            Q(p_description__icontains=q)
        )

    categories = Product.objects.values_list("p_category", flat=True).distinct()

    return render(request, "product.html", {
        "products": products,
        "categories": categories,
        "query": q,
    })


def detail_product(request, id):
    product_obj = get_object_or_404(Product, id=id)
    return render(request, "detail_page.html", {"product": product_obj})


@login_required
def rate_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    stars = int(request.POST.get("rating"))

    ProductRating.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={"stars": stars}
    )

    stats = ProductRating.objects.filter(product=product).aggregate(
        avg=Avg("stars"),
        count=Count("id")
    )

    product.rating = round(stats["avg"] or 0, 1)
    product.rating_count = stats["count"]
    product.save()

    return redirect("detail_page", id=product_id)


@staff_member_required
def add_products(request):
    form = productForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        form.save()
        return redirect("product")
    return render(request, "add_product.html", {"form": form})


@staff_member_required
def edit_products(request, id):
    product_obj = get_object_or_404(Product, id=id)
    form = productForm(request.POST or None, request.FILES or None, instance=product_obj)
    if form.is_valid():
        form.save()
        return redirect("product")
    return render(request, "edit_product.html", {"form": form})


@staff_member_required
def delete_product(request, id):
    product_obj = get_object_or_404(Product, id=id)
    if request.method == "POST":
        product_obj.delete()
        return redirect("product")
    return render(request, "delete_product.html", {"product": product_obj})


@staff_member_required
def toggle_stock(request, id):
    product = get_object_or_404(Product, id=id)
    product.in_stock = not product.in_stock
    product.save()
    return redirect("detail_page", id=id)
