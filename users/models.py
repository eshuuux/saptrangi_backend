from django.db import models
from django.utils import timezone
from datetime import timedelta


# =============================================================
# USER MODEL — Primary Account Table
# =============================================================
class User(models.Model):

    # 🔹 Basic user details
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name  = models.CharField(max_length=100, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True, unique=True)
    mobile     = models.CharField(max_length=10, unique=True)   # 🔥 must be unique
    gender     = models.CharField(max_length=10, blank=True, null=True)

    # 🔹 Optional details
    dob         = models.DateField(blank=True, null=True)       # better than CharField
    profile_pic = models.URLField(blank=True, null=True)        # Cloudinary URL later

    # 🔹 Account Meta
    is_active   = models.BooleanField(default=True)              # soft disable users if needed
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.mobile



# =============================================================
# OTP MODEL — For Login Verification
# =============================================================
class OTP(models.Model):
    mobile     = models.CharField(max_length=10, db_index=True)     # indexed for faster lookup
    code       = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        db_table = "otp_codes"
        ordering = ["-created_at"]

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)  # OTP Validity = 5 mins

    def __str__(self):
        return f"{self.mobile} - {self.code}"


class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    name = models.CharField(max_length=100)          # Full name of receiver
    mobile = models.CharField(max_length=10)         # Delivery mobile number
    pincode = models.CharField(max_length=10)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    house_no = models.CharField(max_length=255)      # Flat / Home / Building
    area = models.CharField(max_length=255)          # Area / street / colony
    address_type = models.CharField(max_length=20, choices=[
        ("Home", "Home"),
        ("Work", "Work"),
        ("Other", "Other")
    ], default="Home")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"

    def __str__(self):
        return f"{self.user.mobile} - {self.city}"
