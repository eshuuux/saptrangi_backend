from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAdminUser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader

from .models import Carousel, Product, Banner, ProductImage
from .serializers import CarouselSerializer, BannerSerializer, ProductSerializer


def upload_to_cloudinary(file, folder):
    upload = cloudinary.uploader.upload(file, folder=folder)
    return upload.get("secure_url")


# ===================== CAROUSEL =====================
@method_decorator(csrf_exempt, name="dispatch")
class CarouselView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        return Response(CarouselSerializer(Carousel.objects.all(), many=True).data)

    def post(self, request):
        self.permission_classes = [IsAdminUser]
        data = request.data.copy()

        if "desktop_image" in request.FILES:
            data["desktop_image"] = upload_to_cloudinary(
                request.FILES["desktop_image"], "carousel/desktop/"
            )
        if "mobile_image" in request.FILES:
            data["mobile_image"] = upload_to_cloudinary(
                request.FILES["mobile_image"], "carousel/mobile/"
            )

        serializer = CarouselSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        self.permission_classes = [IsAdminUser]
        cid = request.data.get("id")
        Carousel.objects.filter(id=cid).delete()
        return Response({"message": "Deleted"})


# ===================== PRODUCT =====================
@method_decorator(csrf_exempt, name="dispatch")
class ProductView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        products = Product.objects.all()

        category = request.GET.get("category")
        search = request.GET.get("search")
        sort = request.GET.get("sort")

        if category:
            products = products.filter(category__icontains=category)
        if search:
            products = products.filter(name__icontains=search)

        if sort == "price_low":
            products = products.order_by("price")
        elif sort == "price_high":
            products = products.order_by("-price")
        elif sort == "newest":
            products = products.order_by("-id")

        return Response(ProductSerializer(products, many=True).data)

    def post(self, request):
        self.permission_classes = [IsAdminUser]
        data = request.data.copy()

        if "main_image" in request.FILES:
            data["main_image"] = upload_to_cloudinary(
                request.FILES["main_image"], "products/main/"
            )

        if "hover_image" in request.FILES:
            data["hover_image"] = upload_to_cloudinary(
                request.FILES["hover_image"], "products/hover/"
            )

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            product = serializer.save()

            # 🔹 Handle multiple gallery images
            gallery_images = request.FILES.getlist("gallery_images")
            for img in gallery_images:
                url = upload_to_cloudinary(img, "products/gallery/")
                ProductImage.objects.create(
                    product=product,
                    image_url=url
                )

            return Response(ProductSerializer(product).data, status=201)

        return Response(serializer.errors, status=400)

    def put(self, request):
        self.permission_classes = [IsAdminUser]
        slug = request.data.get("slug")

        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response({"error": "Not found"}, status=404)

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request):
        self.permission_classes = [IsAdminUser]
        slug = request.data.get("slug")
        Product.objects.filter(slug=slug).delete()
        return Response({"message": "Deleted"})


# ===================== BANNER =====================
@method_decorator(csrf_exempt, name="dispatch")
class BannerView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def get(self, request):
        return Response(BannerSerializer(Banner.objects.all(), many=True).data)

    def post(self, request):
        self.permission_classes = [IsAdminUser]
        data = request.data.copy()

        if "banner_image" in request.FILES:
            data["banner_image"] = upload_to_cloudinary(
                request.FILES["banner_image"], "banners/"
            )

        serializer = BannerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

class HomeView(APIView):
    def get(self, request):
        # 🔹 Carousel images
        carousel = list(
            Carousel.objects.all()[:4].values(
                "desktop_image",
                "mobile_image"
            )
        )

        # 🔹 Top Picks products
        top_picks = list(
            Product.objects.filter(top_picks=True)
            .order_by("-id")[:12]
            .values(
                "name",
                "price",
                "mrp",
                "discount",
                "rating",
                "main_image",
                "hover_image",
                "slug"
            )
        )

        # 🔹 Homepage banners
        banners = list(
            Banner.objects.all().values(
                "name",
                "category",
                "banner_image"
            )
        )

        # 🔹 Category-wise product grouping (for homepage sections)
        products_by_category = {}

        for banner in banners:
            category = banner["category"]
            if not category:
                continue

            products_by_category[category] = list(
                Product.objects.filter(category=category)
                .order_by("-id")[:10]
                .values(
                    "name",
                    "price",
                    "mrp",
                    "discount",
                    "rating",
                    "main_image",
                    "hover_image",
                    "slug"
                )
            )

        return Response(
            {
                "carousel": carousel,
                "top_picks": top_picks,
                "banners": banners,
                "products_by_category": products_by_category
            },
            status=200
        )
    
class ProductDetailBySlug(APIView):
    """
    GET product details using slug
    URL: /products/products/<slug>/
    """

    def get(self, request, slug):
        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class ProductDetailByCategory(APIView):
    """
    GET products by category
    URL: /products/products/category/<category>/
    """

    def get(self, request, category):
        products = Product.objects.filter(
            category__iexact=category
        ).order_by("-id")

        if not products.exists():
            return Response(
                {"message": "No products found for this category"},
                status=status.HTTP_200_OK
            )

        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)