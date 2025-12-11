import random
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken

from django.utils import timezone
from .models import User, OTP, Address
from .serializers import UserSerializer, AddressSerializer



# =============================================================
# USER PROFILE (JWT Protected)
# =============================================================
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Return logged-in user profile"""
        user = request.user  # Retrieved from token
        return Response(UserSerializer(user).data, status=200)



# =============================================================
# UPDATE USER PROFILE (JWT Protected)
# =============================================================
class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Update profile fields except mobile"""
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response({
                "message": "Profile Updated Successfully",
                "data": serializer.data
            }, status=200)

        return Response(serializer.errors, status=400)



# =============================================================
# SEND OTP FOR LOGIN / REGISTER
# =============================================================
class SendOTPView(APIView):
    def post(self, request):
        mobile = request.data.get("mobile")

        if not mobile:
            return Response({"error": "Mobile is required"}, status=400)

        if len(mobile) != 10 or not mobile.isdigit():
            return Response({"error": "Enter valid 10 digit mobile number"}, status=400)

        # Generate six digit OTP 🔥
        code = str(random.randint(100000, 999999))

        OTP.objects.create(mobile=mobile, code=code)

        # TODO → Integrate MSG91 here
        print("OTP for Testing:", code)   # remove once MSG91 integrated

        return Response({
            "message": "OTP sent successfully",
            "mobile": mobile,
            "otp_demo": code   # remove later in production
        }, status=200)



# =============================================================
# VERIFY OTP → LOGIN OR REGISTER + JWT ISSUE
# =============================================================
class VerifyOTPView(APIView):
    def post(self, request):
        mobile = request.data.get("mobile")
        code = request.data.get("otp")

        if not mobile or not code:
            return Response({"error": "Mobile + OTP required"}, status=400)

        try:
            otp_obj = OTP.objects.filter(mobile=mobile, code=code, is_used=False).latest("created_at")
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp_obj.is_expired():
            return Response({"error": "OTP Expired"}, status=400)

        otp_obj.is_used = True
        otp_obj.save()

        # Create user if not exists
        user, created = User.objects.get_or_create(mobile=mobile)

        # Generate JWT Tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "message": "Logged in Successfully" if not created else "Registered + Logged in",
            "user": UserSerializer(user).data,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }, status=200)


class AddressView(APIView):
    permission_classes = [IsAuthenticated]

    # Create New Address
    def post(self, request):
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Address Added", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

    # List All Addresses
    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        return Response(AddressSerializer(addresses, many=True).data, status=200)

    # Update Address
    def put(self, request):
        address_id = request.data.get("id")
        if not address_id:
            return Response({"error": "Address ID required"}, status=400)

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)

        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Address Updated", "data": serializer.data}, status=200)
        return Response(serializer.errors, status=400)

    # Delete Address
    def delete(self, request):
        address_id = request.data.get("id")

        try:
            Address.objects.get(id=address_id, user=request.user).delete()
            return Response({"message": "Address Deleted"}, status=200)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)
