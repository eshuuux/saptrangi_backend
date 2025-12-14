import random
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .utils import send_otp_msg91
from .models import OTP, Address
from .serializers import UserSerializer, AddressSerializer

User = get_user_model()


# =============================================================
# USER PROFILE (JWT Protected)
# =============================================================
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(UserSerializer(user).data, status=200)


# =============================================================
# UPDATE USER PROFILE (JWT Protected)
# =============================================================
class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profile Updated Successfully",
                    "data": serializer.data,
                },
                status=200,
            )

        return Response(serializer.errors, status=400)


# =============================================================
# SEND OTP
# =============================================================
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile")

        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            return Response({"error": "Invalid mobile number"}, status=400)

        # Invalidate old OTPs
        OTP.objects.filter(mobile=mobile, is_used=False).update(is_used=True)

        otp = str(random.randint(100000, 999999))

        OTP.objects.create(
            mobile=mobile,
            code=otp,
        )

        sent = send_otp_msg91(mobile, otp)

        if not sent:
            return Response({"error": "Failed to send OTP"}, status=500)

        return Response({"message": "OTP sent successfully"}, status=200)


# =============================================================
# VERIFY OTP → LOGIN / REGISTER + JWT ISSUE
# =============================================================
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile")
        code = request.data.get("otp")

        if not mobile or not code:
            return Response({"error": "Mobile + OTP required"}, status=400)

        try:
            otp_obj = OTP.objects.filter(
                mobile=mobile,
                code=code,
                is_used=False,
            ).latest("created_at")
        except OTP.DoesNotExist:
            return Response({"error": "Invalid OTP"}, status=400)

        if otp_obj.is_expired():
            return Response({"error": "OTP Expired"}, status=400)

        otp_obj.is_used = True
        otp_obj.save()

        # Create or fetch user
        user, created = User.objects.get_or_create(mobile=mobile)

        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        response = Response(
            {
                "message": "Registered + Logged in" if created else "Logged in Successfully",
                "user": UserSerializer(user).data,
                "accessToken": access_token,
            },
            status=200,
        )

        # 🔐 SET REFRESH TOKEN IN HTTPONLY COOKIE
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=True,      # REQUIRED on Render
            samesite="None",  # REQUIRED for cross-origin
            max_age=7 * 24 * 60 * 60,  # 7 days
        )

        return response


# =============================================================
# REFRESH TOKEN → NEW ACCESS TOKEN
# =============================================================
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)

            user_id = refresh["user_id"]
            user = User.objects.get(id=user_id)

            return Response(
                {
                    "accessToken": access_token,
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except TokenError:
            return Response(
                {"detail": "Invalid or expired refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


# =============================================================
# ADDRESS CRUD (JWT Protected)
# =============================================================
class AddressView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Address Added", "data": serializer.data},
                status=201,
            )
        return Response(serializer.errors, status=400)

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        return Response(
            AddressSerializer(addresses, many=True).data,
            status=200,
        )

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
            return Response(
                {"message": "Address Updated", "data": serializer.data},
                status=200,
            )
        return Response(serializer.errors, status=400)

    def delete(self, request):
        address_id = request.data.get("id")

        try:
            Address.objects.get(id=address_id, user=request.user).delete()
            return Response({"message": "Address Deleted"}, status=200)
        except Address.DoesNotExist:
            return Response({"error": "Address not found"}, status=404)
