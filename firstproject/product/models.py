from django.db import models
from cloudinary.models import CloudinaryField

class Product(models.Model):
    p_name = models.CharField(max_length=200)
    p_category = models.CharField(max_length=200)
    p_description = models.TextField()
    p_link = models.URLField(blank=True, null=True)
    p_price = models.DecimalField(max_digits=10, decimal_places=2)

    # main image - Cloudinary
    p_image = CloudinaryField('image', folder='products', blank=True, null=True)

    # extra images - Cloudinary
    p_image2 = CloudinaryField('image', folder='products', blank=True, null=True)
    p_image3 = CloudinaryField('image', folder='products', blank=True, null=True)
    p_image4 = CloudinaryField('image', folder='products', blank=True, null=True)

    def __str__(self):
        return self.p_name
