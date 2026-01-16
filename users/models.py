from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager


# =============================================================
# USER MANAGER
# =============================================================
class UserManager(BaseUserManager):
    def create_user(self, mobile, password=None, **extra_fields):
        if not mobile:
            raise ValueError("Mobile number is required")

        user = self.model(mobile=mobile, **extra_fields)
        user.set_password(password or None)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(mobile, password, **extra_fields)


# =============================================================
# USER MODEL (OTP BASED + AUTH COMPATIBLE)
# =============================================================
class User(AbstractBaseUser, PermissionsMixin):
    mobile = models.CharField(max_length=10, unique=True)

    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name  = models.CharField(max_length=100, blank=True, null=True)
    email      = models.EmailField(blank=True, null=True)
    gender     = models.CharField(max_length=10, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff  = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "mobile"
    REQUIRED_FIELDS = []

    class Meta:
        db_table = "users"
        ordering = ["-created_at"]

    def __str__(self):
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

    def __str__(self):
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
    street = models.CharField(max_length=255)
    landmark = models.CharField(max_length=255)
    area = models.CharField(max_length=255)
    address_type = models.CharField(max_length=20, default="Home")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "addresses"

    def __str__(self):
        return f"{self.user.mobile} - {self.city}"

class Admin(models.Model) :
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "admin"
    
    def __str__(self):
        return f"Admin ({self.email})"
