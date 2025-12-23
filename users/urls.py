from django.urls import path
from .views import (
    SendOTPView,
    VerifyOTPView,
    ProfileView,
    UpdateProfile,
    AddressView,
    RefreshTokenView
)

urlpatterns = [
    # AUTH
    path("send-otp/", SendOTPView.as_view()),
    path("verify-otp/", VerifyOTPView.as_view()),
    path("refresh/", RefreshTokenView.as_view()),

    # USER
    path("me/", ProfileView.as_view()),
    path("me/update/", UpdateProfile.as_view()),

    # ADDRESS
    path("addresses/", AddressView.as_view()),
]