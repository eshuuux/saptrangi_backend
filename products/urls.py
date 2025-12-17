from django.urls import path
from .views import (
    CarouselView, ProductView, BannerView, HomeView,
    ProductDetailBySlug, ProductDetailByCategory
)

urlpatterns = [
    path("home/", HomeView.as_view()),
    path("banners/", BannerView.as_view()),
    path("carousel/", CarouselView.as_view()),
    path("category/<str:category>/", ProductDetailByCategory.as_view()),
    path("details/<slug:slug>/", ProductDetailBySlug.as_view()),  # GET
    path("/admin", ProductView.as_view()),                      # GET, POST
]

