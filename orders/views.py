from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from django.conf import settings

from .models import Cart, Order, OrderItem, Payment
from .serializers import CartSerializer, OrderSerializer
from products.models import Product
from users.models import Address

import razorpay


from rest_framework.permissions import IsAdminUser


class AdminUpdateOrderStatus(APIView):
    """
    Admin can update order status:
    Pending → Confirmed → Shipped → Out for Delivery → Delivered → Cancelled
    """
    permission_classes = [IsAuthenticated]  # later you can change to IsAdminUser

    def put(self, request):
        order_id = request.data.get("order_id")
        status_value = request.data.get("status")

        if not order_id or not status_value:
            return Response(
                {"error": "order_id and status are required"},
                status=400
            )

        valid_statuses = [
            "Pending",
            "Confirmed",
            "Shipped",
            "Out for Delivery",
            "Delivered",
            "Cancelled"
        ]

        if status_value not in valid_statuses:
            return Response(
                {"error": "Invalid status"},
                status=400
            )

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=404
            )

        order.status = status_value
        order.save()

        return Response(
            {
                "message": "Order status updated successfully",
                "order": OrderSerializer(order).data
            },
            status=200
        )




# ======================================================================
# 🛒 ADD PRODUCT TO CART
# ======================================================================
class AddToCartView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        product_id = request.data.get("product_id")
        size = request.data.get("size")
        quantity = int(request.data.get("quantity", 1))

        if not product_id or not size:
            return Response(
                {"error": "product_id and size are required"},
                status=400
            )

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Invalid product"}, status=404)

        cart_item, created = Cart.objects.get_or_create(
            user=user,
            product=product,
            size=size
        )

        cart_item.quantity = cart_item.quantity + quantity if not created else quantity
        cart_item.save()

        return Response(
            {
                "message": "Added to cart",
                "cart": CartSerializer(cart_item).data
            },
            status=200
        )


# ======================================================================
# 🛍 VIEW CART
# ======================================================================
class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart_items = Cart.objects.filter(user=request.user)
        return Response(
            {"cart": CartSerializer(cart_items, many=True).data},
            status=200
        )



# ======================================================================
# 🔁 UPDATE QUANTITY (SIZE NOT REQUIRED HERE)
# ======================================================================
class UpdateCartQuantityView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        cart_id = request.data.get("cart_id")
        quantity = request.data.get("quantity")

        if not cart_id or quantity is None:
            return Response(
                {"error": "cart_id and quantity required"},
                status=400
            )

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

        return Response(
            {"message": "Quantity updated", "cart": CartSerializer(cart).data},
            status=200
        )


# ======================================================================
# 🔁 UPDATE SIZE (MERGE LOGIC)
# ======================================================================
class UpdateCartSizeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        cart_id = request.data.get("cart_id")
        new_size = request.data.get("size")

        if not cart_id or not new_size:
            return Response(
                {"error": "cart_id and size required"},
                status=400
            )

        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
        except Cart.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=404)

        # Check if same product + new size exists
        existing_item = Cart.objects.filter(
            user=request.user,
            product=cart_item.product,
            size=new_size
        ).exclude(id=cart_item.id).first()

        if existing_item:
            existing_item.quantity += cart_item.quantity
            existing_item.save()
            cart_item.delete()

            return Response(
                {"message": "Size updated & items merged"},
                status=200
            )

        cart_item.size = new_size
        cart_item.save()

        return Response(
            {"message": "Size updated successfully"},
            status=200
        )


# ======================================================================
# ❌ REMOVE CART ITEM
# ======================================================================
class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, cart_id):
        if not cart_id:
            return Response({"error": "cart_id required"}, status=400)

        try:
            cart = Cart.objects.get(id=cart_id, user=request.user)
            cart.delete()
            return Response({"message": "Item removed"}, status=200)
        except Cart.DoesNotExist:
            return Response({"error": "Item not found"}, status=404)


# ======================================================================
# ⚡ BUY NOW (SIZE REQUIRED)
# ======================================================================
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
                {"error": "product_id, size and address_id are required"},
                status=400
            )

        try:
            product = Product.objects.get(id=product_id)
            address = Address.objects.get(id=address_id, user=request.user)
        except (Product.DoesNotExist, Address.DoesNotExist):
            return Response({"error": "Invalid product or address"}, status=404)

        quantity = max(1, quantity)
        total = product.price * quantity

        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            address=address
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


# ======================================================================
# 📦 PLACE ORDER FROM CART
# ======================================================================
class PlaceOrderFromCartView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        user = request.user
        address_id = request.data.get("address_id")

        if not address_id:
            return Response({"error": "address_id required"}, status=400)

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=404)

        cart_items = Cart.objects.filter(user=user)
        if not cart_items.exists():
            return Response({"error": "Cart is empty"}, status=400)

        total = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=user,
            total_amount=total,
            address=address
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


# ======================================================================
# 📜 USER ORDERS
# ======================================================================
class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-id")
        return Response(
            {"orders": OrderSerializer(orders, many=True).data},
            status=200
        )


# ======================================================================
# 🔍 ORDER DETAIL
# ======================================================================
class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        return Response(
            {"order": OrderSerializer(order).data},
            status=200
        )


# ======================================================================
# 💳 RAZORPAY
# ======================================================================
class CreateRazorpayOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")

        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": int(order.total_amount * 100),
            "currency": "INR",
            "payment_capture": 1
        })

        Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order["id"]
        )

        return Response({
            "key": settings.RAZORPAY_KEY_ID,
            "order_id": razorpay_order["id"],
            "amount": order.total_amount,
            "currency": "INR"
        }, status=200)
class VerifyRazorpayPayment(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not razorpay_order_id or not razorpay_payment_id or not razorpay_signature:
            return Response(
                {"error": "Missing payment details"},
                status=400
            )

        try:
            payment = Payment.objects.get(
                razorpay_order_id=razorpay_order_id
            )
        except Payment.DoesNotExist:
            return Response(
                {"error": "Payment record not found"},
                status=404
            )

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        try:
            client.utility.verify_payment_signature({
                "razorpay_order_id": razorpay_order_id,
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_signature": razorpay_signature,
            })
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Payment verification failed"},
                status=400
            )

        # ✅ Mark payment success
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature
        payment.is_paid = True
        payment.save()

        # ✅ Update order status
        order = payment.order
        order.status = "Confirmed"
        order.save()

        return Response(
            {"message": "Payment verified successfully"},
            status=200
        )
