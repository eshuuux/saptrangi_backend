# delivery/urls.py
from django.urls import path
from .views import UploadPincodeCSVView, CheckPincodeView

urlpatterns = [
    path("pincodes/upload/", UploadPincodeCSVView.as_view()),
    path("pincodes/check/", CheckPincodeView.as_view()),
]
