from rest_framework.views import APIView
from rest_framework.response import Response
import cloudinary.uploader
from rest_framework import status
from .models import Carousel,Product,Banner
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import CarouselSerializer, BannerSerializer, ProductSerializer

@method_decorator(csrf_exempt, name='dispatch')
class CarouselView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data.copy()
        desktop_img = request.FILES.get('desktop_image')
        mobile_img = request.FILES.get('mobile_image')

        if desktop_img:
            upload_d = cloudinary.uploader.upload(desktop_img, folder="carousel/desktop/")
            data['desktop_image'] = upload_d['secure_url']

        if mobile_img:
            upload_m = cloudinary.uploader.upload(mobile_img, folder="carousel/mobile/")
            data['mobile_image'] = upload_m['secure_url']

        serializer = CarouselSerializer(data=data)
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
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        data = request.data.copy()
        main_img = request.FILES.get("main_image")
        hover_img = request.FILES.get("hover_image")

        # Upload main image
        if main_img:
            upload1 = cloudinary.uploader.upload(main_img, folder="products/main/")
            data["main_image"] = upload1["secure_url"]

        # Upload hover image
        if hover_img:
            upload2 = cloudinary.uploader.upload(hover_img, folder="products/hover/")
            data["hover_image"] = upload2["secure_url"]
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
           serializer.save()
           return Response({"message":"created", "data":serializer.data}, status=201)
        return Response(serializer.errors, status=400)
           
    def get(self, request):
        products=Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response({"products": serializer.data})
    
@method_decorator(csrf_exempt, name='dispatch')
class BannerView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request):
        data = request.data.copy()
        image = request.FILES.get('banner_image')

        if image:
            upload= cloudinary.uploader.upload(
                image,
                folder="banners/",
                use_filename=True,
                unique_filename=False
            )
            data['banner_image'] = upload['secure_url']

        serializer = BannerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"created", "data":serializer.data}, status=201)
        return Response(serializer.errors, status=400)
    
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
            "name","price","mrp","discount","rating","main_image","hover_image","slug"
        )
        banners = Banner.objects.all().order_by('-id').values(
            "name","category","banner_image"
        )

        products_by_banner={}
        for banner in banners:
            category = banner["category"]
            products = Product.objects.filter(category=category).order_by('-id')[:10].values(
                "name","price","mrp","discount","rating","main_image","hover_image","slug"
            )
            products_by_banner[category]=list(products)
        return Response({
            "carousel":list(carousel),
            "top_picks":list(top_picks),
            "banners":list(banners),
            "product_by_banner":products_by_banner
        },status=200)
    
@method_decorator(csrf_exempt, name='dispatch')
class ProductDetailBySlug(APIView):
    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)
        
@method_decorator(csrf_exempt, name='dispatch')
class ProductDetailByCategory(APIView):
    def get(self, request, category):
        products = Product.objects.filter(category=category)

        if products.exists():
            serializer = ProductSerializer(products, many=True) 
            return Response(serializer.data)

        return Response({"error": "No products found"}, status=404)