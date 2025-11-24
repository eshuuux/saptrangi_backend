from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.

class Carousel(models.Model):
    name=models.CharField(max_length=100)
    desktop_image=models.URLField(max_length=500)       # Desktop Image
    mobile_image=models.URLField(max_length=500)       # Mobile Image
    class Meta():
        db_table='carousel'

class Product(models.Model):
    name=models.CharField(max_length=100)
    mrp=models.IntegerField()     # Maximum Retail Price
    price=models.IntegerField()        #SLUGGINATION, INSTAED OF SPACE ADD - , ALSO ALL LOWERCASE () ANOTHER COLUMN.
    rating=models.FloatField()
    discount=models.IntegerField()
    product_images=ArrayField(models.URLField(max_length=500), blank=True, default=list)
    category=models.CharField(max_length=100)
    top_picks=models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta():
        db_table='product'
    
class Banner(models.Model):
    name=models.CharField(max_length=100)
    banner_image=models.URLField(max_length=500)    # Banner Image
    class Meta():
        db_table='banner'