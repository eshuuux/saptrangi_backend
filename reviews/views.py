from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Avg

from .models import Review
from .serializers import ReviewSerializer
from products.models import Product
from orders.models import OrderItem


# =============================================================
# ADD / UPDATE REVIEW
# =============================================================
class AddOrUpdateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        user = request.user
        rating = request.data.get("rating")
        comment = request.data.get("comment", "")

        # -------- VALIDATION --------
        if not rating:
            return Response({"error": "Rating is required"}, status=400)

        rating = int(rating)
        if rating < 1 or rating > 5:
            return Response({"error": "Rating must be between 1 and 5"}, status=400)

        # -------- PRODUCT CHECK --------
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        # -------- PURCHASE CHECK --------
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status="DELIVERED"
        ).exists()

        if not has_purchased:
            return Response(
                {"error": "You can review only purchased products"},
                status=403
            )

        # -------- CREATE OR UPDATE REVIEW --------
        review, created = Review.objects.update_or_create(
            user=user,
            product=product,
            defaults={
                "rating": rating,
                "comment": comment
            }
        )

        # -------- UPDATE PRODUCT RATING --------
        avg_rating = Review.objects.filter(product=product).aggregate(
            Avg("rating")
        )["rating__avg"]

        product.rating = round(avg_rating, 1)
        product.save(update_fields=["rating"])

        serializer = ReviewSerializer(review)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


# =============================================================
# LIST REVIEWS FOR A PRODUCT
# =============================================================
class ProductReviewListView(APIView):
    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id)
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)


# =============================================================
# DELETE REVIEW (USER OR ADMIN)
# =============================================================
class DeleteReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id):
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)

        # Allow owner or admin
        if review.user != request.user and not request.user.is_staff:
            return Response({"error": "Permission denied"}, status=403)

        product = review.product
        review.delete()

        # Recalculate rating
        avg_rating = Review.objects.filter(product=product).aggregate(
            Avg("rating")
        )["rating__avg"]

        product.rating = round(avg_rating, 1) if avg_rating else 0
        product.save(update_fields=["rating"])

        return Response({"message": "Review deleted"}, status=200)
