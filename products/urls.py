from django.urls import path
from .views import (
    CarouselView, ProductView, BannerView, HomeView,
    ProductDetailBySlug, ProductDetailByCategory
)

urlpatterns = [
    # ------------------ HOMEPAGE ROUTES ------------------ #
    path("home/", HomeView.as_view(), name="home-data"),  # All homepage data
    # ------------------ PRODUCT ROUTES ------------------- #
    path("products/", ProductView.as_view(), name="all-products"),  # GET + POST
    path("products/<slug:slug>/", ProductDetailBySlug.as_view(), name="product-detail"),
    path("products/category/<str:category>/", ProductDetailByCategory.as_view(), name="product-by-category"),
    # ------------------ BANNER & CAROUSEL ---------------- #
    path("banners/", BannerView.as_view(), name="banners"),
    path("carousel/", CarouselView.as_view(), name="carousel"),
]
