from django.shortcuts import render
# payments/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings
import razorpay

from orders.models import Order
from .models import Payment


# Create your views here.
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
