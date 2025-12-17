from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import cloudinary.uploader

from .models import Carousel, Product, Banner
from .serializers import CarouselSerializer, BannerSerializer, ProductSerializer


# =============================================================
# UTILITY → UPLOAD IMAGE TO CLOUDINARY (REUSABLE)
# =============================================================
def upload_to_cloudinary(file, folder):
    """Reusable cloudinary uploader for all image uploads."""
    upload = cloudinary.uploader.upload(file, folder=folder)
    return upload.get("secure_url", None)


# =============================================================
# CAROUSEL VIEW
# =============================================================
@method_decorator(csrf_exempt, name="dispatch")
class CarouselView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        data = request.data.copy()
        desktop = request.FILES.get("desktop_image")
        mobile = request.FILES.get("mobile_image")

        # Upload to cloudinary
        if desktop:
            data["desktop_image"] = upload_to_cloudinary(desktop, "carousel/desktop/")
        if mobile:
            data["mobile_image"] = upload_to_cloudinary(mobile, "carousel/mobile/")

        serializer = CarouselSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Carousel Created", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

    def get(self, request):
        carousels = Carousel.objects.all()
        return Response(CarouselSerializer(carousels, many=True).data)
    
    def delete(self, request):
        carousel_id = request.data.get("id")
        if not carousel_id:
            return Response({"error": "Carousel 'id' required for delete"}, status=400)

        try:
            Carousel.objects.get(id=carousel_id).delete()
            return Response({"message": "Carousel Deleted Successfully"})
        except Carousel.DoesNotExist:
            return Response({"error": "Carousel not found"}, status=404)


# =============================================================
# PRODUCT CRUD + IMAGE UPLOAD
# =============================================================
@method_decorator(csrf_exempt, name="dispatch")
class ProductView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    # ---------------- CREATE PRODUCT ---------------- #
    def post(self, request):
        data = request.data.copy()

        if "main_image" in request.FILES:
            data["main_image"] = upload_to_cloudinary(request.FILES["main_image"], "products/main/")
        if "hover_image" in request.FILES:
            data["hover_image"] = upload_to_cloudinary(request.FILES["hover_image"], "products/hover/")

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message":"Product Created", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


    # ---------------- READ / FILTER PRODUCTS ---------------- #
    def get(self, request):
        products = Product.objects.all()

        # 🔥 Filters
        category = request.GET.get("category")
        rating = request.GET.get("rating")           # min rating products
        size = request.GET.get("size")
        price_min = request.GET.get("min_price")
        price_max = request.GET.get("max_price")
        search = request.GET.get("search")
        sort = request.GET.get("sort")               # price_low | price_high | newest

        if category: products = products.filter(category__icontains=category)
        if rating: products = products.filter(rating__gte=float(rating))
        if size: products = products.filter(size__icontains=size)
        if price_min: products = products.filter(price__gte=int(price_min))
        if price_max: products = products.filter(price__lte=int(price_max))
        if search: products = products.filter(name__icontains=search)

        # 🔥 Sorting
        if sort == "price_low": products = products.order_by("price")
        if sort == "price_high": products = products.order_by("-price")
        if sort == "newest": products = products.order_by("-id")

        return Response(ProductSerializer(products, many=True).data)


    # ---------------- UPDATE PRODUCT ---------------- #
    def put(self, request):
        slug = request.data.get("slug")
        if not slug:
            return Response({"error": "Slug required for update"}, status=400)

        try:
            product = Product.objects.get(slug=slug)
        except Product.DoesNotExist:
            return Response({"error": "Product Not Found"}, status=404)

        data = request.data.copy()

        # Optional new image update
        if "main_image" in request.FILES:
            data["main_image"] = upload_to_cloudinary(request.FILES["main_image"], "products/main/")
        if "hover_image" in request.FILES:
            data["hover_image"] = upload_to_cloudinary(request.FILES["hover_image"], "products/hover/")

        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Product Updated", "product": serializer.data})
        return Response(serializer.errors, status=400)


    # ---------------- DELETE PRODUCT ---------------- #
    def delete(self, request):
        slug = request.data.get("slug")

        if not slug:
            return Response({"error": "Slug required to delete"}, status=400)

        try:
            Product.objects.get(slug=slug).delete()
            return Response({"message": "Product Deleted Successfully"}, status=200)
        except Product.DoesNotExist:
            return Response({"error": "Product Not Found"}, status=404)

# =============================================================
# BANNER MODEL VIEW
# =============================================================
@method_decorator(csrf_exempt, name="dispatch")
class BannerView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    # ---------------- CREATE BANNER ---------------- #
    def post(self, request):
        data = request.data.copy()

        if "banner_image" in request.FILES:
            data["banner_image"] = upload_to_cloudinary(request.FILES["banner_image"], "banners/")

        serializer = BannerSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Banner Created", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)


    # ---------------- GET ALL BANNERS ---------------- #
    def get(self, request):
        return Response(BannerSerializer(Banner.objects.all(), many=True).data)


    # ---------------- UPDATE BANNER ---------------- #
    def put(self, request):
        banner_id = request.data.get("id")
        if not banner_id:
            return Response({"error": "Banner 'id' required for update"}, status=400)

        try:
            banner = Banner.objects.get(id=banner_id)
        except Banner.DoesNotExist:
            return Response({"error": "Banner not found"}, status=404)

        data = request.data.copy()
        if "banner_image" in request.FILES:
            data["banner_image"] = upload_to_cloudinary(request.FILES["banner_image"], "banners/")

        serializer = BannerSerializer(banner, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Banner Updated", "data": serializer.data})
        return Response(serializer.errors, status=400)


    # ---------------- DELETE BANNER ---------------- #
    def delete(self, request):
        banner_id = request.data.get("id")
        if not banner_id:
            return Response({"error": "Banner 'id' required for delete"}, status=400)

        try:
            Banner.objects.get(id=banner_id).delete()
            return Response({"message": "Banner Deleted Successfully"})
        except Banner.DoesNotExist:
            return Response({"error": "Banner not found"}, status=404)

        
# =============================================================
# HOME API → CAROUSEL + BANNERS + TOP PICKS + CATEGORY WISE
# =============================================================
class HomeView(APIView):
    def get(self, request):
        carousel = list(Carousel.objects.all()[:4].values("desktop_image", "mobile_image"))
        top_picks = list(Product.objects.filter(top_picks=True).order_by("-id")[:12].values(
            "name","price","mrp","discount","rating","main_image","hover_image","slug"
        ))
        banners = list(Banner.objects.all().values("name","category","banner_image"))

        # Category-wise grouped products for homepage
        product_map = {}
        for b in banners:
            product_map[b["category"]] = list(
                Product.objects.filter(category=b["category"])[:10].values(
                    "name","price","mrp","discount","rating","main_image","hover_image","slug"))
        return Response({
            "carousel" : carousel,
            "top_picks" : top_picks,
            "banners" : banners,
            "products_by_category" : product_map
        }, status=200)

# =============================================================
# PRODUCT DETAIL BY SLUG
# =============================================================
class ProductDetailBySlug(APIView):
    def get(self, request, slug):
        try:
            return Response(ProductSerializer(Product.objects.get(slug=slug)).data)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

# =============================================================
# PRODUCT LIST BY CATEGORY
# =============================================================
class ProductDetailByCategory(APIView):
    def get(self, request, category):
        products = Product.objects.filter(category=category)
        if not products.exists():
            return Response({"error": "No products found"}, status=404)
        return Response(ProductSerializer(products, many=True).data)