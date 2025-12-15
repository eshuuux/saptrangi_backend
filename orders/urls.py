from django.urls import path
from .views import (
    AddToCartView,
    CartView,
    UpdateCartView,
    RemoveCartItemView,
    BuyNowView,
    PlaceOrderFromCartView,
    OrderListView,
    OrderDetailView,
    CreateRazorpayOrder,
    VerifyRazorpayPayment,
    AdminUpdateOrderStatus,
    UpdateCartSizeView,        # 🔥 NEW
)

urlpatterns = [

    # ===================== 🛒 CART ===================== #
    path("cart/add/", AddToCartView.as_view(), name="add-to-cart"),
    path("cart/", CartView.as_view(), name="view-cart"),

    # 🔁 Update quantity only
    path(
        "cart/update-quantity/",
        UpdateCartView.as_view(),
        name="update-cart-quantity"
    ),

    # 🔁 Update size only (NEW)
    path(
        "cart/update-size/",
        UpdateCartSizeView.as_view(),
        name="update-cart-size"
    ),

    # ❌ Remove item
    path(
        "cart/remove/",
        RemoveCartItemView.as_view(),
        name="remove-cart-item"
    ),


    # ===================== 📦 ORDERS ==================== #
    path("order/buy/", BuyNowView.as_view(), name="buy-now"),
    path("order/place/", PlaceOrderFromCartView.as_view(), name="place-order"),
    path("orders/", OrderListView.as_view(), name="order-list"),
    path("orders/<int:order_id>/", OrderDetailView.as_view(), name="order-detail"),


    # ===================== 💳 PAYMENTS ================== #
    path("payment/create/", CreateRazorpayOrder.as_view(), name="create-razorpay-order"),
    path("payment/verify/", VerifyRazorpayPayment.as_view(), name="verify-razorpay-payment"),


    # ===================== 🛠 ADMIN ===================== #
    path(
        "admin/order/update-status/",
        AdminUpdateOrderStatus.as_view(),
        name="admin-update-order-status"
    ),
]
