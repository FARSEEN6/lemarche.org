from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Product(models.Model):
    p_name = models.CharField(max_length=200)
    p_category = models.CharField(max_length=200)
    p_description = models.TextField()
    p_price = models.DecimalField(max_digits=10, decimal_places=2)

    in_stock = models.BooleanField(default=True)

    p_image = CloudinaryField('image', folder='products', blank=True, null=True)
    p_image2 = CloudinaryField('image', folder='products', blank=True, null=True)

    rating = models.FloatField(default=0)
    rating_count = models.IntegerField(default=0)

    def __str__(self):
        return self.p_name


class ProductRating(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="ratings")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField()

    class Meta:
        unique_together = ("product", "user")
