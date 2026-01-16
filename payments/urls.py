from django.urls import path
from .views import (
    CreateRazorpayOrder,
    razorpay_callback,
    razorpay_webhook,
    OrderStatusAPIView
)

urlpatterns = [
    path("razorpay/create/", CreateRazorpayOrder.as_view()),
    path("razorpay/callback/", razorpay_callback),
    path("razorpay/webhook/", razorpay_webhook),
    path("order-status/<int:order_id>/", OrderStatusAPIView.as_view()),
]