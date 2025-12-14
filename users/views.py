import random
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny

from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .models import OTP, Address
from .serializers import UserSerializer, AddressSerializer

User = get_user_model()

# =============================================================
# USER PROFILE (JWT Protected)
# =============================================================
class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            UserSerializer(request.user).data,
            status=status.HTTP_200_OK
        )

# =============================================================
# UPDATE USER PROFILE (JWT Protected)
# =============================================================
class UpdateProfile(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = UserSerializer(
            request.user,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Profile Updated Successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# =============================================================
# SEND OTP (DEV MODE – OTP SHOWN IN RESPONSE)
# =============================================================
class SendOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile")

        # Validate mobile
        if not mobile or len(mobile) != 10 or not mobile.isdigit():
            return Response(
                {"error": "Invalid mobile number"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Invalidate previous OTPs
        OTP.objects.filter(
            mobile=mobile,
            is_used=False
        ).update(is_used=True)

        # Generate OTP
        otp = str(random.randint(100000, 999999))

        OTP.objects.create(
            mobile=mobile,
            code=otp
        )

        # DEV RESPONSE (OTP VISIBLE)
        return Response(
            {
                "message": "OTP sent (DEV MODE)",
                "mobile": mobile,
                "otp": otp
            },
            status=status.HTTP_200_OK
        )

# =============================================================
# VERIFY OTP → LOGIN / REGISTER + JWT
# =============================================================
class VerifyOTPView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        mobile = request.data.get("mobile")
        otp_code = request.data.get("otp")

        if not mobile or not otp_code:
            return Response(
                {"error": "Mobile and OTP are required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        otp_obj = OTP.objects.filter(
            mobile=mobile,
            code=otp_code,
            is_used=False
        ).first()

        if not otp_obj:
            return Response(
                {"error": "Invalid OTP"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if otp_obj.is_expired():
            return Response(
                {"error": "OTP expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Mark OTP used
        otp_obj.is_used = True
        otp_obj.save(update_fields=["is_used"])

        # Create or get user
        user, created = User.objects.get_or_create(mobile=mobile)

        try:
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
        except TokenError:
            return Response(
                {"error": "Token generation failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        response = Response(
            {
                "message": "Registered + Logged in" if created else "Logged in Successfully",
                "user": UserSerializer(user).data,
                "accessToken": access_token,
            },
            status=status.HTTP_200_OK
        )

        # Refresh token cookie
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=not settings.DEBUG,
            samesite="None" if not settings.DEBUG else "Lax",
            max_age=7 * 24 * 60 * 60,
        )

        return response

# =============================================================
# REFRESH ACCESS TOKEN
# =============================================================
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"error": "Refresh token not found"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
            user = User.objects.get(id=refresh["user_id"])

            return Response(
                {
                    "accessToken": access_token,
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK
            )

        except (TokenError, User.DoesNotExist):
            return Response(
                {"error": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
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
                status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        addresses = Address.objects.filter(user=request.user)
        return Response(
            AddressSerializer(addresses, many=True).data,
            status=status.HTTP_200_OK
        )

    def put(self, request):
        address_id = request.data.get("id")

        if not address_id:
            return Response(
                {"error": "Address ID required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            address = Address.objects.get(id=address_id, user=request.user)
        except Address.DoesNotExist:
            return Response(
                {"error": "Address not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Address Updated", "data": serializer.data},
                status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        address_id = request.data.get("id")

        try:
            Address.objects.get(id=address_id, user=request.user).delete()
            return Response(
                {"message": "Address Deleted"},
                status=status.HTTP_200_OK
            )
        except Address.DoesNotExist:
            return Response(
                {"error": "Address not found"},
                status=status.HTTP_404_NOT_FOUND
            )
