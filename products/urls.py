from .import views
from django.urls import path
from django.contrib import admin
from .views import *

urlpatterns = [
    path('carousel/',CarouselView.as_view()),
    path('product/',ProductView.as_view()),
    path('banner/',BannerView.as_view()),
    path('home/',HomeView.as_view()),
    path('<slug:slug>/',ProductDetailBySlug.as_view()),
    path('category/<str:category>/',ProductDetailByCategory.as_view())
]