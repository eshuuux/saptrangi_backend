from rest_framework import serializers
from .models import User, Address

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer handles:
    ✔ Return user data after login
    ✔ Profile update (except mobile)
    ✔ Future safe for address/order linking
    """

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['mobile', 'created_at']   # mobile login only — not editable


    # ---------------- OPTIONAL VALIDATION ---------------- #
    # If later you allow mobile update, this activates.
    def validate_mobile(self, value):
        if len(value) != 10 or not value.isdigit():
            raise serializers.ValidationError("Mobile number must be 10 digits")
        return value

    def validate(self, data):
        # Add rules here whenever needed later
        return data

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = "__all__"
        read_only_fields = ["user"]
