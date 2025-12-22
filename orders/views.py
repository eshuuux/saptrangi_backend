from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db import transaction

from .models import Cart, Order, OrderItem
from .serializers import CartSerializer, OrderSerializer
from products.models import Product
from users.models import Address


# ==================================================
# 🛒 ADD TO CART
# ==================================================
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get("product_id")
        size = request.data.get("size")
        quantity = int(request.data.get("quantity", 1))

        if not product_id or not size:
            return Response(
                {"error": "product_id and size required"},
                status=400
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Invalid product"}, status=404)

        if quantity < 1:
            return Response({"error": "Invalid quantity"}, status=400)

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            size=size
        )

        cart_item.quantity = (
            cart_item.quantity + quantity if not created else quantity
        )
        cart_item.save()

        return Response(
            {"message": "Added to cart", "cart": CartSerializer(cart_item).data},
            status=200
        )


# ==================================================
# 🛍 VIEW CART
# ==================================================
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        return Response(
            {"cart": CartSerializer(cart_items, many=True).data},
            status=200
        )


# ==================================================
# 🔁 UPDATE QUANTITY
# ==================================================
class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        cart_id = request.data.get("cart_id")
        quantity = request.data.get("quantity")

        if not cart_id or quantity is None:
            return Response({"error": "cart_id and quantity required"}, status=400)

        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)

        quantity = int(quantity)
        if quantity < 1:
            cart.delete()
            return Response({"message": "Item removed"}, status=200)

        cart.quantity = quantity
        cart.save()

        return Response({"message": "Quantity updated"}, status=200)


# ==================================================
# 🔁 UPDATE SIZE (MERGE SAFE)
# ==================================================
class UpdateCartSizeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        cart_id = request.data.get("cart_id")
        new_size = request.data.get("size")

        if not cart_id or not new_size:
            return Response({"error": "cart_id and size required"}, status=400)

        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)

        existing = Cart.objects.filter(
            user=request.user,
            product=cart_item.product,
            size=new_size
        ).exclude(id=cart_item.id).first()

        if existing:
            existing.quantity += cart_item.quantity
            existing.save()
            cart_item.delete()
        else:
            cart_item.size = new_size
            cart_item.save()

        return Response({"message": "Size updated"}, status=200)


# ==================================================
# ❌ REMOVE CART ITEM
# ==================================================
class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_id):
        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
            cart.delete()
            return Response({"message": "Item removed"}, status=200)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)


# ==================================================
# ⚡ BUY NOW
# ==================================================
class BuyNowView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        product_id = request.data.get("product_id")
        size = request.data.get("size")
        quantity = int(request.data.get("quantity", 1))
        address_id = request.data.get("address_id")

        if not product_id or not size or not address_id:
            return Response(
                {"error": "product_id, size, address_id required"},
                status=400
            )

        try:
            product = Product.objects.get(id=product_id)
            address = Address.objects.get(id=address_id, user=request.user)
        except (Product.DoesNotExist, Address.DoesNotExist):
            return Response({"error": "Invalid product or address"}, status=404)

        total = product.price * max(1, quantity)

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            size=size,
            quantity=quantity,
            price=product.price
        )

        return Response(
            {"message": "Order created", "order": OrderSerializer(order).data},
            status=201
        )


# ==================================================
# 📦 PLACE ORDER FROM CART
# ==================================================
class PlaceOrderFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        address_id = request.data.get("address_id")

        if not address_id:
            return Response({"error": "address_id required"}, status=400)

        try:
            address = Address.objects.get(
                id=address_id,
                user=request.user
            )
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=404)

        cart_items = Cart.objects.filter(user=request.user).select_related("product")
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = 0
        for item in cart_items:
            total += item.product.price * item.quantity

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                size=item.size,
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()

        return Response(
            {"message": "Order placed", "order": OrderSerializer(order).data},
            status=201
        )


# ==================================================
# 📜 USER ORDERS
# ==================================================
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        return Response(
            {"orders": OrderSerializer(orders, many=True).data},
            status=200
        )


# ==================================================
# 🔍 ORDER DETAIL
# ==================================================
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        return Response(
            {"order": OrderSerializer(order).data},
            status=200
        )


# ==================================================
# 🛠 ADMIN UPDATE STATUS
# ==================================================
class AdminUpdateOrderStatus(APIView):
    permission_classes = [IsAdminUser]

    def put(self, request):
        order_id = request.data.get("order_id")
        status_value = request.data.get("status")

        valid_statuses = [
            "PENDING",
            "CONFIRMED",
            "SHIPPED",
            "OUT_FOR_DELIVERY",
            "DELIVERED",
            "CANCELLED",
        ]

        if not order_id or status_value not in valid_statuses:
            return Response({"error": "Invalid data"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.status = status_value
        order.save()

        return Response(
            {"message": "Order status updated"},
            status=200
        )
