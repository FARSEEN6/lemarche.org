# product/context_processors.py
from .models import Product

def categories_processor(request):
    categories = (
        Product.objects
        .values_list('p_category', flat=True)
        .distinct()
        .order_by('p_category')
    )
    return {
        "nav_categories": categories
    }
