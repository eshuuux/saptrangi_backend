from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from django.shortcuts import get_object_or_404

from textblob import TextBlob

from .models import Review
from .serializers import ReviewSerializer
from products.models import Product
from orders.models import OrderItem

# =============================================================
# 🔹 AI SCORE UTILITY
# =============================================================
def calculate_ai_score(comment: str, rating: int) -> float:

    if not comment:
        sentiment_score = 0
        length_score = 0
    else:
        sentiment_score = TextBlob(comment).sentiment.polarity  # -1 to +1
        length_score = min(len(comment) / 200, 1)               # max 1

    ai_score = (
        (sentiment_score * 0.5) +
        (rating * 0.3) +
        (length_score * 0.2)
    )

    return round(ai_score, 2)


# =============================================================
# ✅ ADD OR UPDATE REVIEW
# =============================================================
class AddOrUpdateReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, product_id):
        user = request.user
        rating = request.data.get("rating")
        comment = request.data.get("comment", "").strip()

        # ---------- VALIDATION ----------
        if rating is None:
            return Response(
                {"error": "Rating is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            rating = int(rating)
        except ValueError:
            return Response(
                {"error": "Rating must be an integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if rating < 1 or rating > 5:
            return Response(
                {"error": "Rating must be between 1 and 5"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # ---------- PRODUCT ----------
        product = get_object_or_404(Product, id=product_id)

        # ---------- VERIFIED PURCHASE CHECK ----------
        has_purchased = OrderItem.objects.filter(
            order__user=user,
            product=product,
            order__status="DELIVERED"
        ).exists()

        if not has_purchased:
            return Response(
                {"error": "You can review only purchased products"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ---------- AI SCORE ----------
        ai_score = calculate_ai_score(comment, rating)

        # ---------- CREATE / UPDATE ----------
        review, created = Review.objects.update_or_create(
            user=user,
            product=product,
            defaults={
                "rating": rating,
                "comment": comment,
                "ai_score": ai_score
            }
        )

        serializer = ReviewSerializer(review)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
        )


# =============================================================
# 📋 LIST REVIEWS FOR A PRODUCT (AI SORTED)
# =============================================================
class ProductReviewListView(APIView):

    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)

        reviews = Review.objects.filter(
            product=product
        ).order_by("-ai_score", "-created_at")

        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


# =============================================================
# ❌ DELETE REVIEW (USER OR ADMIN)
# =============================================================
class DeleteReviewView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        # ---------- PERMISSION ----------
        if review.user != request.user and not request.user.is_staff:
            return Response(
                {"error": "Permission denied"},
                status=status.HTTP_403_FORBIDDEN
            )

        review.delete()

        return Response(
            {"message": "Review deleted successfully"},
            status=status.HTTP_200_OK
        )