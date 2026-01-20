from django.urls import path
from .views import home


# Create your tests here.
urlpatterns = [
    path('',home)
]