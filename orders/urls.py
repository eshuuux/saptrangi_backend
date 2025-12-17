from django.urls import path
from .views import (
    AddToCartView,
    CartView,
    UpdateCartQuantityView,
    UpdateCartSizeView,
    RemoveCartItemView,
    BuyNowView,
    PlaceOrderFromCartView,
    OrderListView,
    OrderDetailView,
    AdminUpdateOrderStatus,
)

urlpatterns = [
    # CART
    path("", CartView.as_view()),                      # GET
    path("add/", AddToCartView.as_view()),           # POST
    path("update/quantity/", UpdateCartQuantityView.as_view()),
    path("update/size/", UpdateCartSizeView.as_view()),
    path("remove/<int:cart_id>/", RemoveCartItemView.as_view()),

    # ORDERS
    path("", OrderListView.as_view()),                  # GET
    path("<int:order_id>/", OrderDetailView.as_view()),
    path("buy-now/", BuyNowView.as_view()),
    path("checkout/", PlaceOrderFromCartView.as_view()),
]