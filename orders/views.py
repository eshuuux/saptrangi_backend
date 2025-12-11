from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Cart, Order, OrderItem
from products.models import Product
from .serializers import CartSerializer, OrderSerializer



# ======================================================================
# 🛒 ADD PRODUCT TO CART
# ======================================================================
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "product_id is required"}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Invalid Product ID"}, status=404)

        cart_item, created = Cart.objects.get_or_create(user=user, product=product)

        cart_item.quantity = cart_item.quantity + quantity if not created else quantity
        cart_item.save()

        return Response({"message": "Added to cart", "cart": CartSerializer(cart_item).data}, status=200)



# ======================================================================
# 🛍 VIEW CART ITEMS
# ======================================================================
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        return Response({"cart": CartSerializer(cart_items, many=True).data}, status=200)



# ======================================================================
# 🔁 UPDATE QUANTITY
# ======================================================================
class UpdateCartView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        cart_id = request.data.get("cart_id")
        quantity = request.data.get("quantity")

        if not cart_id or not quantity:
            return Response({"error": "cart_id & quantity required"}, status=400)

        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found in cart"}, status=404)

        quantity = int(quantity)

        if quantity < 1:
            cart.delete()
            return Response({"message": "Item removed from cart"}, status=200)

        cart.quantity = quantity
        cart.save()
        return Response({"message": "Cart updated", "cart": CartSerializer(cart).data}, status=200)



# ======================================================================
# ❌ REMOVE ITEM FROM CART
# ======================================================================
class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart_id = request.data.get("cart_id")

        if not cart_id:
            return Response({"error": "cart_id required"}, status=400)

        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
            cart.delete()
            return Response({"message": "Item removed"}, status=200)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)



# ======================================================================
# ⚡ BUY NOW (Instant Order — Skip Cart)
# ======================================================================
class BuyNowView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        if not product_id:
            return Response({"error": "product_id is required"}, status=400)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Invalid Product ID"}, status=404)

        order = Order.objects.create(
            user=request.user,
            total_amount=product.price * quantity
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price  # snapshot
        )

        return Response({"message": "Order placed successfully", "order": OrderSerializer(order).data}, status=201)



# ======================================================================
# 📦 PLACE ORDER FROM CART
# ======================================================================
class PlaceOrderFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(user=request.user, total_amount=total)

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()
        return Response({"message": "Order placed", "order": OrderSerializer(order).data}, status=201)



# ======================================================================
# 📜 USER ORDER LIST
# ======================================================================
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-id")
        return Response({"orders": OrderSerializer(orders, many=True).data}, status=200)



# ======================================================================
# 🔍 ORDER DETAILS WITH ITEMS
# ======================================================================
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        return Response({"order": OrderSerializer(order).data}, status=200)
