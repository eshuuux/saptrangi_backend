from django.urls import path
from .views import (
    CarouselView, ProductView, BannerView, HomeView,
    ProductDetailBySlug, ProductDetailByCategory
)

urlpatterns = [
    path("", ProductView.as_view()),                      # GET, POST
    path("<slug:slug>/", ProductDetailBySlug.as_view()),  # GET
    path("category/<str:category>/", ProductDetailByCategory.as_view()),
    path("home/", HomeView.as_view()),
    path("banners/", BannerView.as_view()),
    path("carousel/", CarouselView.as_view()),
]

