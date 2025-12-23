from django.urls import path
from .views import (
    CreateRazorpayOrder,
    VerifyRazorpayPayment,
    razorpay_webhook
)

urlpatterns = [
    path("razorpay/create/", CreateRazorpayOrder.as_view()),
    path("razorpay/verify/", VerifyRazorpayPayment.as_view()),
    path("razorpay/webhook/", razorpay_webhook),
]