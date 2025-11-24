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
        body = request.data
        c = Carousel.objects.create(
            name=body.get('name'),
            desktop_image=body.get('desktop_img'),
            mobile_image=body.get('mobile_img')
        )
        return Response({"message": "Added!", "id": c.id})
    
    from .serializers import CarouselSerializer, BannerSerializer

def get(self, request):
    carousels = Carousel.objects.all()
    serializer = CarouselSerializer(carousels, many=True)
    return Response({"carousels": serializer.data})


@method_decorator(csrf_exempt, name='dispatch')
class ProductView(APIView):
    
    def post(self, request):
        body=request.data
        p=Product.objects.create(
            name=body.get('name'),
            mrp=body.get('mrp'),
            price=body.get('price'),
            rating=body.get('rating'),
            discount=body.get('discount'),
            product_images=body.get('images'),
            category=body.get('category'),
            top_picks=body.get('top_picks')
        )
        return Response({"message": "product added !"})
    
    def get(self, request):
        products=Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response({"products": serializer.data})
    
@method_decorator(csrf_exempt, name='dispatch')
class BannerView(APIView):

    def post(self, request):
        body=request.data
        b=Banner.objects.create(
            name=body.get('name'),
            banner_image=body.get('banner_image'),
        )
        return Response({"message": "banner added", "id":b.id })
    
    def get(self, request):
        banners = Banner.objects.all()
        serializer = BannerSerializer(banners, many=True)
        return Response({"banners": serializer.data})
