from django.db import models
from django.utils import timezone
from datetime import timedelta


# =============================================================
# USER MODEL (SIMPLE – OTP BASED)
# =============================================================
class User(models.Model):
    mobile = models.CharField(max_length=10, unique=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name  = models.CharField(max_length=100, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True)
    gender     = models.CharField(max_length=10, blank=True, null=True)

    is_active  = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def _str_(self):
        return self.mobile


# =============================================================
# OTP MODEL
# =============================================================
class OTP(models.Model):
    mobile     = models.CharField(max_length=10, db_index=True)
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        db_table = "otp_codes"
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def _str_(self):
        return f"{self.mobile} - {self.code}"


# =============================================================
# ADDRESS MODEL
# =============================================================
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")

    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=10)
    pincode = models.CharField(max_length=10)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    house_no = models.CharField(max_length=255)
    area = models.CharField(max_length=255)

    address_type = models.CharField(
        max_length=20,
        choices=[
            ("Home", "Home"),
            ("Work", "Work"),
            ("Other", "Other")
        ],
        default="Home"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"

    def _str_(self):
        return f"{self.user.mobile} - {self.city}"