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
class HomeView(APIView):

    def get(self,request):
        carousel = Carousel.objects.all().order_by('-id')[:2].values(
            "desktop_image","mobile_image"
        )
        top_picks = Product.objects.filter(top_picks=True).order_by('-id').values(
            "name","price","mrp","discount","rating","product_images","slug"
        )
        banners = Banner.objects.all().order_by('-id').values(
            "name","category","banner_image"
        )

        products_by_banner={}
        for banner in banners:
            category = banner["category"]
            products = Product.objects.filter(category=category).order_by('-id')[:10].values(
                "name","price","mrp","discount","rating","product_images","slug"
            )
            products_by_banner[category]=list(products)
        return Response({
            "carousel":list(carousel),
            "top_picks":list(top_picks),
            "banners":list(banners),
            "product_by_banner":products_by_banner
        },status=200)
    
class ProductDetailBySlug(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)