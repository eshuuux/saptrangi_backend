from rest_framework import serializers
from .models import Cart, Order, OrderItem
from products.serializers import ProductSerializer
from users.serializers import AddressSerializer

# ============================ CART SERIALIZER ============================ #
class CartSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = Cart
        fields = ["id", "product", "quantity", "product_details"]
        read_only_fields = ["id"]


# ======================== ORDER ITEMS SERIALIZER ======================== #
class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ["product", "quantity", "price"]



# ============================ ORDER SERIALIZER =========================== #
class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_items = serializers.SerializerMethodField()   # 🔥 new dynamic field
    address = AddressSerializer(read_only=True)   # NEW


    class Meta:
        model = Order
        fields = ["id", "total_amount", "total_items", "status", "created_at", "address", "items"]

    def get_total_items(self, obj):
        return obj.items.count()  # count number of products in order
