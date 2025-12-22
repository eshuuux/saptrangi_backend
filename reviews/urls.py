from django.urls import path
from .views import (
    AddOrUpdateReviewView,
    ProductReviewListView,
    DeleteReviewView
)

urlpatterns = [
    path("product/<int:product_id>/", ProductReviewListView.as_view()),
    path("product/<int:product_id>/add/", AddOrUpdateReviewView.as_view()),
    path("delete/<int:review_id>/", DeleteReviewView.as_view()),
]
