from rest_framework import serializers
from .models import Carousel, Product, Banner


# =============================================================
# CAROUSEL SERIALIZER
# =============================================================
class CarouselSerializer(serializers.ModelSerializer):
    """
    For homepage slider (desktop + mobile images).
    Simple serializer, no heavy logic needed yet.
    """

    class Meta:
        model = Carousel
        fields = "__all__"



# =============================================================
# PRODUCT SERIALIZER (Main Product API Handling)
# =============================================================
class ProductSerializer(serializers.ModelSerializer):
    """
    Controls product create/read/update.
    Auto-slug generated from model, so slug must be read_only.
    Extra calculated fields added (optional use later).
    """

    # Auto-calculated price after discount (Optional UI improvement)
    discounted_price = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["slug", "created_at"]  # user should not update these

    # ---------------------------------------------------------
    # CALCULATE EFFECTIVE PRICE IF NEEDED (UI Booster)
    # ---------------------------------------------------------
    def get_discounted_price(self, obj):
        try:
            # Example: price after discount use for frontend
            return obj.mrp - (obj.mrp * obj.discount / 100)
        except:
            return obj.price    # fallback safety

    # ---------------------------------------------------------
    # VALIDATION (Improves data quality)
    # ---------------------------------------------------------
    def validate(self, data):
        """
        Prevent wrong data input.
        Examples:
        - Price should never be more than MRP
        - Rating must remain between 0 and 5
        """

        if "price" in data and "mrp" in data:
            if data["price"] > data["mrp"]:
                raise serializers.ValidationError("Selling price cannot be greater than MRP ⚠")

        if "rating" in data and (data["rating"] < 0 or data["rating"] > 5):
            raise serializers.ValidationError("Rating must be between 0 and 5 ⭐")

        return data



# =============================================================
# BANNER SERIALIZER (Homepage Wide Banner)
# =============================================================
class BannerSerializer(serializers.ModelSerializer):
    """
    Used for homepage promotional banner images + category mapping
    """
    class Meta:
        model = Banner
        fields = "__all__"
