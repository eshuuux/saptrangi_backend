import uuid
from django.db import models
from django.utils.text import slugify
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator

# Create your models here.

class Carousel(models.Model):
    name=models.CharField(max_length=100)
    desktop_image=models.URLField(max_length=500)       # Desktop Image
    mobile_image=models.URLField(max_length=500)       # Mobile Image
    class Meta():
        db_table='carousel'

class Product(models.Model):
    name=models.CharField(max_length=100)
    mrp=models.IntegerField()     
    price=models.IntegerField()      
    rating=models.FloatField()
    discount=models.IntegerField()
    main_image = models.URLField(blank=True)
    hover_image = models.URLField(blank=True)
    category=models.CharField(max_length=100)
    fabric = models.CharField(max_length=100, blank=True)
    size = models.CharField(max_length=100, blank=True)
    slug = models.CharField(max_length=150, unique=True, blank=True)
    quantity = models.IntegerField(blank=True,null=True)
    comfort = models.CharField(max_length=100, blank=True)
    occasion = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True, null=True)
    top_picks =  models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta():
        db_table='product'

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_id = uuid.uuid4().hex[:6]  # 6-digit professional hash
            self.slug = f"{base_slug}-{unique_id}"  # example: classic-white-tee-a3b4c1
        super().save(*args, **kwargs)

class Banner(models.Model):
    name=models.CharField(max_length=100)
    category=models.CharField(max_length=100, blank=True)
    banner_image=models.URLField(max_length=500)    # Banner Image
    class Meta():
        db_table='banner'