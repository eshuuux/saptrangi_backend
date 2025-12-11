import uuid
from django.db import models
from django.utils.text import slugify


# =============================================================
# CAROUSEL MODEL → For Home Hero Slider
# =============================================================
class Carousel(models.Model):
    name = models.CharField(max_length=100)
    desktop_image = models.URLField(max_length=500)    # Desktop banner
    mobile_image = models.URLField(max_length=500)     # Mobile banner version

    class Meta:
        db_table = 'carousel'
        verbose_name = "Carousel Banner"
        verbose_name_plural = "Carousel Banners"

    def __str__(self):
        return self.name



# =============================================================
# PRODUCT MODEL → Core E-commerce Product Table
# =============================================================
class Product(models.Model):

    # 🔹 BASIC PRODUCT DETAILS
    name = models.CharField(max_length=100)
    mrp = models.IntegerField()                        # Original price
    price = models.IntegerField()                      # Selling price (after discount)
    discount = models.IntegerField()                   # Percentage off (optional future automation)
    rating = models.FloatField()                       # Avg rating (can calculate later)
    
    # 🔹 CLOUDINARY IMAGE LINKS
    main_image = models.URLField(blank=True)           # Main product image
    hover_image = models.URLField(blank=True)          # Hover image for UI

    # 🔹 CATEGORY + FILTERING (very important fields)
    category = models.CharField(max_length=100, db_index=True)  # indexed for faster filtering
    fabric = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)         # You can convert to ManyToMany later
    comfort = models.CharField(max_length=100, blank=True)
    occasion = models.CharField(max_length=100, blank=True)

    # 🔹 SEO + URL HANDLING
    slug = models.CharField(max_length=150, unique=True, blank=True)

    # 🔹 INVENTORY MANAGEMENT
    quantity = models.IntegerField(blank=True, null=True)       # Stock
    description = models.TextField(blank=True, null=True)

    # 🔹 HOME UI HIGHLIGHT TAGS
    top_picks = models.BooleanField(default=False)

    # 🔹 AUTOMATIC FIELDS
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'product'
        ordering = ['-created_at']      # Latest products first
        verbose_name = "Product"
        verbose_name_plural = "Products"

    def __str__(self):
        return self.name


    # ---------------------------------------------------------
    # AUTO-GENERATE SLUG IF EMPTY
    # ---------------------------------------------------------
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_id = uuid.uuid4().hex[:6]  # Short & clean unique suffix
            self.slug = f"{base_slug}-{unique_id}"  # Ex: cotton-kurti-a3b5d9
        super().save(*args, **kwargs)



# =============================================================
# HOME BANNER (Wide Horizontal Home Image)
# =============================================================
class Banner(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    banner_image = models.URLField(max_length=500)      # Cloudinary URL

    class Meta:
        db_table = 'banner'
        verbose_name = "Homepage Banner"
        verbose_name_plural = "Homepage Banners"

    def __str__(self):
        return self.name
