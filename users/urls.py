from django.urls import path
from .views import SendOTPView, VerifyOTPView, ProfileView, UpdateProfile, AddressView, RefreshTokenView

urlpatterns = [

    # ---------- OTP AUTH ROUTES ---------- #
    path("auth/send-otp/", SendOTPView.as_view(), name="send-otp"),
    path("auth/verify-otp/", VerifyOTPView.as_view(), name="verify-otp"),

    # ---------- USER PROFILE ROUTES ---------- #
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/update/", UpdateProfile.as_view(), name="update-profile"),

    path("address/", AddressView.as_view(), name="user-address"),
    path("auth/refresh", RefreshTokenView.as_view(), name="token-refresh"),
]
