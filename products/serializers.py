from rest_framework import serializers

from .models import Category, Product, Inventory, Review


# =======================================================
# CATEGORY SERIALIZER
# =======================================================

class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category

        fields = [
            'id',
            'name',
            'description',
            'is_active',
            'created_at',
        ]

        read_only_fields = [
            'id',
            'created_at',
        ]


# =======================================================
# INVENTORY SERIALIZER
# =======================================================

class InventorySerializer(serializers.ModelSerializer):

    available_quantity = serializers.ReadOnlyField()

    is_low_stock = serializers.ReadOnlyField()

    class Meta:
        model = Inventory

        fields = [
            'id',
            'product',
            'quantity',
            'reserved_quantity',
            'available_quantity',
            'low_stock_threshold',
            'is_low_stock',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'available_quantity',
            'is_low_stock',
            'updated_at',
        ]


# =======================================================
# PRODUCT SERIALIZER
# =======================================================

class ProductSerializer(serializers.ModelSerializer):

    category_name = serializers.CharField(
        source='category.name',
        read_only=True
    )

    inventory = InventorySerializer(
        read_only=True
    )

    class Meta:
        model = Product

        fields = [
            'id',
            'category',
            'category_name',
            'name',
            'sku',
            'description',
            'price',
            'stock',
            'is_active',
            'inventory',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'category_name',
            'inventory',
            'created_at',
            'updated_at',
        ]


# =======================================================
# REVIEW SERIALIZER
# =======================================================

class ReviewSerializer(serializers.ModelSerializer):

    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = Review

        fields = [
            'id',
            'product',
            'product_name',
            'user_name',
            'rating',
            'comment',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'product_name',
            'user_name',
            'created_at',
            'updated_at',
        ]

    def validate_rating(self, value):

        if value < 1 or value > 5:
            raise serializers.ValidationError(
                'Rating must be between 1 and 5.'
            )

        return value