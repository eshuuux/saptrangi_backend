from rest_framework import serializers
from .models import Carousel, Product, Banner

class CarouselSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carousel
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    read_only_fields = ['slug']
    class Meta:
        model = Product
        fields = '__all__'

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = '__all__'