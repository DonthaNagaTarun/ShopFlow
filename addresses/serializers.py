from rest_framework import serializers

from .models import Address


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

        fields = [
            'id',
            'address_type',
            'full_name',
            'phone_number',
            'address_line',
            'city',
            'state',
            'postal_code',
            'is_default',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]

    def validate_phone_number(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                'Phone number must contain only digits.'
            )

        if len(value) != 10:
            raise serializers.ValidationError(
                'Phone number must be exactly 10 digits.'
            )

        return value

    def validate_postal_code(self, value):

        if not value.isdigit():
            raise serializers.ValidationError(
                'Postal code must contain only digits.'
            )

        if len(value) != 6:
            raise serializers.ValidationError(
                'Postal code must be exactly 6 digits.'
            )

        return value