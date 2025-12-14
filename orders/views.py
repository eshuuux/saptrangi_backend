from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import Cart, Order, OrderItem
from products.models import Product
from .serializers import CartSerializer, OrderSerializer
from users.models import Address

import razorpay
from django.conf import settings
from .models import Payment


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
        address_id = request.data.get("address_id")

        if not address_id:
            return Response({"error": "address_id is required"}, status=400)

        # Validate Address
        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Invalid address"}, status=404)

        # Validate Product
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "Invalid product"}, status=404)

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
            quantity=quantity,
            price=product.price
        )

        return Response({
            "message": "Order Created Successfully",
            "order": OrderSerializer(order).data
        }, status=201)



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
            return Response({"error": "address_id is required"}, status=400)

        # Validate Address
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
                quantity=item.quantity,
                price=item.product.price
            )

        cart_items.delete()

        return Response({
            "message": "Order Placed Successfully",
            "order": OrderSerializer(order).data
        }, status=201)



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

import razorpay
from django.conf import settings
from .models import Payment

class CreateRazorpayOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        order_id = request.data.get("order_id")

        # Validate order
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": int(order.total_amount * 100),   # convert to paise
            "currency": "INR",
            "payment_capture": 1
        })

        # Save razorpay order ID
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
        order_id = request.data.get("order_id")
        payment_id = request.data.get("razorpay_payment_id")
        razorpay_order_id = request.data.get("razorpay_order_id")
        signature = request.data.get("razorpay_signature")

        # Get payment record
        try:
            payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found"}, status=404)

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        # Signature verification
        try:
            client.utility.verify_payment_signature({
                'razorpay_payment_id': payment_id,
                'razorpay_order_id': razorpay_order_id,
                'razorpay_signature': signature
            })
        except:
            return Response({"error": "Signature verification failed"}, status=400)

        # Update payment record
        payment.razorpay_payment_id = payment_id
        payment.razorpay_signature = signature
        payment.is_paid = True
        payment.save()

        # Update order status
        payment.order.status = "Confirmed"
        payment.order.save()

        return Response({"message": "Payment Verified Successfully"}, status=200)

class AdminUpdateOrderStatus(APIView):
    """
    Admin can update order status:
    Pending → Confirmed → Shipped → Out for Delivery → Delivered → Cancelled
    """
    
    # ⚠️ In future you can add admin authentication
    # permission_classes = [IsAdminUser]

    def put(self, request):
        order_id = request.data.get("order_id")
        new_status = request.data.get("status")

        if not order_id or not new_status:
            return Response({"error": "order_id and status required"}, status=400)

        # Check if valid choice
        valid_statuses = [
            "Pending", "Confirmed", "Shipped",
            "Out for Delivery", "Delivered", "Cancelled"
        ]

        if new_status not in valid_statuses:
            return Response({"error": "Invalid status"}, status=400)

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

        order.status = new_status
        order.save()

        return Response({
            "message": "Order status updated",
            "order": OrderSerializer(order).data
        }, status=200)
