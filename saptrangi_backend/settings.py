"""
Django settings for saptrangi_backend project.
"""

from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from datetime import timedelta
import cloudinary
import cloudinary.uploader
import cloudinary.api

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# --------------------------------------------------
# SECURITY
# --------------------------------------------------

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-dev-key")

DEBUG = os.environ.get("DEBUG", "True") == "True"

ALLOWED_HOSTS = ["*"]

# --------------------------------------------------
# APPLICATIONS
# --------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "corsheaders",
    "rest_framework",
    "cloudinary",
    "cloudinary_storage",

    # Local apps
    "users",
    "products",
    "orders",
    "payments",
]

# --------------------------------------------------
# MIDDLEWARE (ORDER MATTERS)
# --------------------------------------------------

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

# --------------------------------------------------
# CORS + CSRF (ENV SAFE)
# --------------------------------------------------

CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "https://saptrangi.netlify.app",
]

CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",
    "https://saptrangi.netlify.app",
]

# 🔐 ENV-BASED COOKIE SETTINGS
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"
SESSION_COOKIE_SAMESITE = "None" if not DEBUG else "Lax"

# --------------------------------------------------
# DJANGO REST FRAMEWORK
# --------------------------------------------------

REST_FRAMEWORK = {
    "DEFAULT_RENDERER_CLASSES": (
        "rest_framework.renderers.JSONRenderer",
    ),
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.AllowAny",
    ),
}

# --------------------------------------------------
# JWT CONFIG
# --------------------------------------------------

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# --------------------------------------------------
# DATABASE
# --------------------------------------------------

DATABASES = {
    "default": dj_database_url.config(
        env="DATABASE_URL",
        default="postgresql://ashish:k0vJbZcMjphSS9140WT38mH9jvdeXlNV@dpg-d4i6f195pdvs739knlbg-a.oregon-postgres.render.com/saptrangi",
        conn_max_age=600,
    )
}

# --------------------------------------------------
# URLS & TEMPLATES
# --------------------------------------------------

ROOT_URLCONF = "saptrangi_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "saptrangi_backend.wsgi.application"

# --------------------------------------------------
# PASSWORD VALIDATION
# --------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --------------------------------------------------
# INTERNATIONALIZATION
# --------------------------------------------------

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --------------------------------------------------
# STATIC & MEDIA (Cloudinary)
# --------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
STATICFILES_STORAGE = "cloudinary_storage.storage.StaticHashedCloudinaryStorage"

cloudinary.config(
    cloud_name="dcskqhiwb",
    api_key="688844436758916",
    api_secret="hdfkwHRw70SkOGP3Zlb4VkRQQzA",
    secure=True,
)

# --------------------------------------------------
# DEFAULT PRIMARY KEY
# --------------------------------------------------

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --------------------------------------------------
# THIRD-PARTY KEYS
# --------------------------------------------------

RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

MSG91_AUTH_KEY = os.getenv("MSG91_AUTH_KEY")
MSG91_SENDER_ID = os.getenv("MSG91_SENDER_ID")
MSG91_TEMPLATE_ID = os.getenv("MSG91_TEMPLATE_ID")
