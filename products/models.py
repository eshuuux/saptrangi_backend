import uuid
from django.db import models
from django.utils.text import slugify


class Carousel(models.Model):
    name = models.CharField(max_length=100)
    desktop_image = models.URLField(max_length=500)
    mobile_image = models.URLField(max_length=500)

    class Meta:
        db_table = "carousel"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)

    mrp = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    discount = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0, editable=False)

    main_image = models.URLField(blank=True)
    hover_image = models.URLField(blank=True)
    category = models.CharField(max_length=100, db_index=True)
    fabric = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    comfort = models.CharField(max_length=100, blank=True)
    occasion = models.CharField(max_length=100, blank=True)

    slug = models.CharField(max_length=150, unique=True, blank=True)

    quantity = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)

    top_picks = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            self.slug = f"{base_slug}-{uuid.uuid4().hex[:6]}"
        super().save(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product_images"

    def __str__(self):
        return f"Image for {self.product.name}"



class Banner(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, blank=True)
    banner_image = models.URLField(max_length=500)

    class Meta:
        db_table = "banner"

    def __str__(self):
        return self.name
