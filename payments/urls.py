# payments/urls.py
from django.urls import path
from .views import CreateRazorpayOrder, VerifyRazorpayPayment

urlpatterns = [
    path("razorpay/create/", CreateRazorpayOrder.as_view()),
    path("razorpay/verify/", VerifyRazorpayPayment.as_view()),
]
