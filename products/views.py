from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Carousel,Product,Banner
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .serializers import CarouselSerializer, BannerSerializer, ProductSerializer

@method_decorator(csrf_exempt, name='dispatch')
class CarouselView(APIView):

    def post(self, request):
        serializer = CarouselSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "created", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        carousels = Carousel.objects.all()
        serializer = CarouselSerializer(carousels, many=True)
        return Response({"carousels": serializer.data})

@method_decorator(csrf_exempt, name='dispatch')
class ProductView(APIView):

    def post(self, request):
       serializer = ProductSerializer(data=request.data)
       if serializer.is_valid():
           serializer.save()
           return Response({"message":"created", "data":serializer.data}, status=201)
       return Response(serializer.error, status=400)
           
    def get(self, request):
        products=Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response({"products": serializer.data})
    
@method_decorator(csrf_exempt, name='dispatch')
class BannerView(APIView):

    def post(self, request):
        serializer = BannerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"created", "data":serializer.data}, status=201)
        return Response(serializer.error, status=400)
    
    def get(self, request):
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response({"banners": serializer.data})
    
@method_decorator(csrf_exempt, name='dispatch')
class OverallView(APIView):

    def get(self,request):
        carousel = Carousel.objects.all()
        product = Product.objects.all()
        banner = Banner.objects.all()

        car_serializer = CarouselSerializer(carousel, many=True)
        pro_serializer = ProductSerializer(product, many=True)
        ban_serializer = BannerSerializer(banner, many=True)

        return Response({"carousel":car_serializer.data,"product":pro_serializer.data,"banner":ban_serializer.data},status=200)