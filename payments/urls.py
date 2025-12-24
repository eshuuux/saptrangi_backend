from django.urls import path
from .views import (
    CreateRazorpayOrder,
    razorpay_callback,
    razorpay_webhook
)

urlpatterns = [
    path("razorpay/create/", CreateRazorpayOrder.as_view()),
    path("razorpay/callback/", razorpay_callback),
    path("razorpay/webhook/", razorpay_webhook),
]