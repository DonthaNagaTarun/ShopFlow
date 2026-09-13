from rest_framework import serializers

from .models import Order, OrderItem, Payment


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'quantity',
            'price',
            'subtotal',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(
        many=True,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'payment_status',
            'total_amount',
            'shipping_address',
            'items',
            'created_at',
            'updated_at',
        ]


class PaymentSerializer(serializers.ModelSerializer):
    order_number = serializers.CharField(
        source='order.order_number',
        read_only=True
    )

    class Meta:
        model = Payment
        fields = [
            'id',
            'order',
            'order_number',
            'payment_method',
            'transaction_id',
            'amount',
            'status',
            'created_at',
            'updated_at',
        ]