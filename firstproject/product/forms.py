from django import forms
from .models import Product


class productForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "p_name",
            "p_category",
            "p_description",
            "p_price",
            "p_image",
            "p_image2",
            "in_stock",
        ]

        widgets = {
            "p_name": forms.TextInput(attrs={"class": "form-control"}),
            "p_category": forms.TextInput(attrs={"class": "form-control"}),
            "p_description": forms.Textarea(
                attrs={"class": "form-control", "rows": 3}
            ),
            "p_price": forms.NumberInput(attrs={"class": "form-control"}),
            "p_image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "p_image2": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
