from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q

from django.contrib.admin.views.decorators import staff_member_required  # ⬅ NEW
from django.contrib.auth.decorators import login_required               # ⬅ optional but useful

from .form import productForm
from .models import Product


def Home(request):
    products = Product.objects.filter(p_name__icontains="mac")
    return render(request, 'home.html', {'products': products})


def product(request):
    q = request.GET.get('q', '').strip()
    category = request.GET.get('category', '').strip()
    sort = request.GET.get('sort', '').strip()

    products = Product.objects.all()

    # 🔍 search
    if q:
        products = products.filter(
            Q(p_name__icontains=q) |
            Q(p_category__icontains=q) |
            Q(p_description__icontains=q)
        )

    # 📂 category filter from navbar dropdown
    if category:
        products = products.filter(p_category__iexact=category)

    # 🔢 optional: sort
    if sort == 'price_asc':
        products = products.order_by('p_price')
    elif sort == 'price_desc':
        products = products.order_by('-p_price')

    categories = Product.objects.values_list('p_category', flat=True).distinct()

    return render(request, 'product.html', {
        'products': products,
        'categories': categories,
        'query': q,
        'selected_category': category,
        'sort': sort,
    })


def detail_product(request, id):
    product_obj = get_object_or_404(Product, id=id)
    return render(request, 'detail_page.html', {'product': product_obj})


# ❌ DELETE PRODUCT – ADMIN/STAF ONLY
@staff_member_required
def delete_product(request, id):
    product_obj = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        product_obj.delete()
        return redirect('product')

    return render(request, 'delete_product.html', {'product': product_obj})


# ➕ ADD PRODUCT – ADMIN/STAF ONLY
@staff_member_required
def add_products(request):
    if request.method == 'POST':
        form = productForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('product')
    else:
        form = productForm()
    return render(request, 'add_product.html', {'form': form})


# ✏ EDIT PRODUCT – ADMIN/STAF ONLY
@staff_member_required
def edit_products(request, id):
    product_obj = get_object_or_404(Product, id=id)

    if request.method == 'POST':
        form = productForm(request.POST, request.FILES, instance=product_obj)
        if form.is_valid():
            form.save()
            return redirect('product')
    else:
        form = productForm(instance=product_obj)

    return render(request, 'edit_product.html', {
        'form': form,
        'product': product_obj
    })
