from .import views
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('carousel',views.carousel),
    path('carousel_data',views.get_carousel),
    path('product',views.product),
    path('product_data',views.get_product),
    path('banner',views.banner),
    path('banner_data',views.get_banner),
]