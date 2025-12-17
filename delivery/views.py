from django.shortcuts import render
import csv
import io

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import DeliveryPincode

class UploadPincodeCSVView(APIView):
    # permission_classes = [IsAuthenticated]  # later: IsAdminUser

    def post(self, request):
        file = request.FILES.get("file")

        if not file:
            return Response({"error": "CSV file required"}, status=400)

        if not file.name.endswith(".csv"):
            return Response({"error": "Only CSV files allowed"}, status=400)

        decoded_file = file.read().decode("utf-8").splitlines()
        reader = csv.DictReader(decoded_file)

        added = 0
        skipped = 0

        for row in reader:
            pincode = row.get("pincode")

            if not pincode:
                skipped += 1
                continue

            obj, created = DeliveryPincode.objects.get_or_create(
                pincode=pincode.strip(),
                defaults={
                    "city": row.get("city", "").strip(),
                    "state": row.get("state", "").strip(),
                    "is_active": row.get("is_active", "1") in ["1", "true", "True"],
                }
            )

            if created:
                added += 1
            else:
                skipped += 1

        return Response({
            "message": "CSV processed successfully",
            "added": added,
            "skipped": skipped
        })

class CheckPincodeView(APIView):
    """
    Check whether delivery is available for a given pincode
    """

    def get(self, request):
        pincode = request.GET.get("pincode")

        if not pincode:
            return Response(
                {"error": "pincode is required"},
                status=400
            )

        if len(pincode) != 6 or not pincode.isdigit():
            return Response(
                {"error": "Invalid pincode format"},
                status=400
            )

        delivery = DeliveryPincode.objects.filter(
            pincode=pincode,
            is_active=True
        ).first()

        if not delivery:
            return Response(
                {
                    "pincode": pincode,
                    "delivery_available": False,
                    "message": "Delivery not available at this location"
                },
                status=200
            )

        return Response(
            {
                "pincode": pincode,
                "delivery_available": True,
                "city": delivery.city,
                "state": delivery.state,
                "message": "Delivery available"
            },
            status=200
        )
