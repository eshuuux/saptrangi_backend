
# import razorpay
# from django.conf import settings
# from django.db import transaction

# from rest_framework.views import APIView
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status

# from orders.models import Order, OrderItem
# from products.models import Product
# from users.models import Address
# from .models import Payment


# import json
# import hmac
# import hashlib
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.conf import settings

# from .models import Payment



# class CreateRazorpayOrder(APIView):
#     permission_classes = [IsAuthenticated]

#     @transaction.atomic
#     def post(self, request):
#         product_id = request.data.get("product_id")
#         size = request.data.get("size")
#         quantity = int(request.data.get("quantity", 1))
#         address_id = request.data.get("address_id")

#         if not product_id or not size or not address_id:
#             return Response(
#                 {"error": "product_id, size, address_id required"},
#                 status=400
#             )

#         try:
#             product = Product.objects.get(id=product_id)
#             address = Address.objects.get(id=address_id, user=request.user)
#         except (Product.DoesNotExist, Address.DoesNotExist):
#             return Response(
#                 {"error": "Invalid product or address"},
#                 status=404
#             )

#         quantity = max(1, quantity)
#         total_rupees = product.price * quantity
#         total_paise = int(total_rupees * 100)

#         # 🔹 Create Order
#         order = Order.objects.create(
#             user=request.user,
#             address=address,
#             total_amount=total_rupees
#         )

#         OrderItem.objects.create(
#             order=order,
#             product=product,
#             size=size,
#             quantity=quantity,
#             price=product.price
#         )

#         # 🔒 Prevent duplicate payment
#         if hasattr(order, "payment"):
#             return Response(
#                 {"error": "Payment already initiated"},
#                 status=400
#             )

#         client = razorpay.Client(
#             auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
#         )

#         razorpay_order = client.order.create({
#             "amount": total_paise,
#             "currency": "INR"
#         })

#         Payment.objects.create(
#             order=order,
#             razorpay_order_id=razorpay_order["id"],
#             status="CREATED"
#         )

#         return Response({
#             "order_id": order.id,
#             "razorpay": {
#                 "key": settings.RAZORPAY_KEY_ID,
#                 "razorpay_order_id": razorpay_order["id"],
#                 "amount": total_paise,   # ⚠️ only sent to frontend
#                 "currency": "INR"
#             }
#         }, status=201)


# class VerifyRazorpayPayment(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         razorpay_order_id = request.data.get("razorpay_order_id")
#         razorpay_payment_id = request.data.get("razorpay_payment_id")
#         razorpay_signature = request.data.get("razorpay_signature")

#         if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
#             return Response(
#                 {"error": "Missing payment details"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         try:
#             payment = Payment.objects.get(
#                 razorpay_order_id=razorpay_order_id
#             )
#         except Payment.DoesNotExist:
#             return Response(
#                 {"error": "Payment not found"},
#                 status=status.HTTP_404_NOT_FOUND
#             )

#         client = razorpay.Client(
#             auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
#         )

#         try:
#             client.utility.verify_payment_signature({
#                 "razorpay_order_id": razorpay_order_id,
#                 "razorpay_payment_id": razorpay_payment_id,
#                 "razorpay_signature": razorpay_signature,
#             })
#         except razorpay.errors.SignatureVerificationError:
#             return Response(
#                 {"error": "Invalid payment signature"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

#         payment.razorpay_payment_id = razorpay_payment_id
#         payment.razorpay_signature = razorpay_signature
#         payment.save()

#         return Response(
#             {"message": "Payment verified. Waiting for webhook."},
#             status=status.HTTP_200_OK
#         )



# @csrf_exempt
# def razorpay_webhook(request):
#     received_signature = request.headers.get("X-Razorpay-Signature")
#     payload = request.body

#     expected_signature = hmac.new(
#         settings.RAZORPAY_WEBHOOK_SECRET.encode(),
#         payload,
#         hashlib.sha256
#     ).hexdigest()

#     if not hmac.compare_digest(received_signature or "", expected_signature):
#         return HttpResponse(status=400)

#     data = json.loads(payload)
#     event = data.get("event")

#     if event == "payment.captured":
#         entity = data["payload"]["payment"]["entity"]
#         razorpay_order_id = entity["order_id"]
#         razorpay_payment_id = entity["id"]

#         try:
#             payment = Payment.objects.get(
#                 razorpay_order_id=razorpay_order_id
#             )

#             if payment.status != "PAID":
#                 payment.status = "PAID"
#                 payment.razorpay_payment_id = razorpay_payment_id
#                 payment.save()

#                 order = payment.order
#                 order.status = "CONFIRMED"
#                 order.save()

#         except Payment.DoesNotExist:
#             pass

#     elif event == "payment.failed":
#         entity = data["payload"]["payment"]["entity"]
#         razorpay_order_id = entity["order_id"]

#         try:
#             payment = Payment.objects.get(
#                 razorpay_order_id=razorpay_order_id
#             )
#             payment.status = "FAILED"
#             payment.save()
#         except Payment.DoesNotExist:
#             pass

#     return HttpResponse(status=200)
import json
import hmac
import hashlib
import razorpay

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from orders.models import Order, OrderItem
from products.models import Product
from users.models import Address
from .models import Payment


# ======================================================
# 💳 CREATE RAZORPAY ORDER (BUY NOW)
# ======================================================
class CreateRazorpayOrder(APIView):
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
            return Response(
                {"error": "Invalid product or address"},
                status=404
            )

        quantity = max(1, quantity)
        total_rupees = product.price * quantity
        total_paise = int(total_rupees * 100)

        # 🧾 Create Order
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total_rupees
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            size=size,
            quantity=quantity,
            price=product.price
        )

        # 🔒 Prevent duplicate payment
        if hasattr(order, "payment"):
            return Response(
                {"error": "Payment already initiated"},
                status=400
            )

        client = razorpay.Client(
            auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
        )

        razorpay_order = client.order.create({
            "amount": total_paise,
            "currency": "INR"
        })

        Payment.objects.create(
            order=order,
            razorpay_order_id=razorpay_order["id"],
            status="CREATED"
        )

        return Response({
            "order_id": order.id,
            "razorpay": {
                "key": settings.RAZORPAY_KEY_ID,
                "razorpay_order_id": razorpay_order["id"],
                "amount": total_paise,
                "currency": "INR"
            }
        }, status=201)


# ======================================================
# ✅ VERIFY PAYMENT (REDIRECT CALLBACK)
# ======================================================
# 
@csrf_exempt
def razorpay_callback(request):
    if request.method != "POST":
        return HttpResponse(status=400)

    razorpay_order_id = request.POST.get("razorpay_order_id")
    razorpay_payment_id = request.POST.get("razorpay_payment_id")
    razorpay_signature = request.POST.get("razorpay_signature")

    if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
        return redirect("https://saptrangi.netlify.app/payment-failed")

    # 🔐 Verify signature
    generated_signature = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        f"{razorpay_order_id}|{razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != razorpay_signature:
        return redirect("https://saptrangi.netlify.app/payment-failed")

    # ✅ Payment verified (DO NOT WAIT FOR FRONTEND)
    try:
        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        payment.status = "PAID"
        payment.razorpay_payment_id = razorpay_payment_id
        payment.save()

        order = payment.order
        order.status = "CONFIRMED"
        order.save()
    except Payment.DoesNotExist:
        pass

    # 🔥 MOST IMPORTANT
    return redirect("https://saptrangi.netlify.app/order-success")
# ======================================================
# 🔔 RAZORPAY WEBHOOK (FINAL AUTHORITY)
# ======================================================
@csrf_exempt
def razorpay_webhook(request):
    received_signature = request.headers.get("X-Razorpay-Signature")
    payload = request.body

    expected_signature = hmac.new(
        settings.RAZORPAY_WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(received_signature or "", expected_signature):
        return HttpResponse(status=400)

    data = json.loads(payload)
    event = data.get("event")

    entity = data.get("payload", {}).get("payment", {}).get("entity", {})
    razorpay_order_id = entity.get("order_id")
    razorpay_payment_id = entity.get("id")

    if not razorpay_order_id:
        return HttpResponse(status=200)

    try:
        payment = Payment.objects.get(
            razorpay_order_id=razorpay_order_id
        )
    except Payment.DoesNotExist:
        return HttpResponse(status=200)

    if event in ["payment.captured", "order.paid"]:
        if payment.status != "PAID":
            payment.status = "PAID"
            payment.razorpay_payment_id = razorpay_payment_id
            payment.save()

            order = payment.order
            order.status = "CONFIRMED"
            order.save()

    elif event == "payment.failed":
        payment.status = "FAILED"
        payment.save()

    return HttpResponse(status=200)

class OrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            return Response({
                "order_id": order.id,
                "status": order.status
            })
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )