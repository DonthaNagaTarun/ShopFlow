import uuid
from decimal import Decimal

from django.db import transaction

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from addresses.models import Address
from cart.models import Cart, CartItem
from products.models import Inventory

from .models import Order, OrderItem, Payment
from .serializers import OrderSerializer, PaymentSerializer
from .permissions import IsStaffOrAdmin


class OrderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        if request.user.role in ['staff', 'admin']:
            orders = Order.objects.all().prefetch_related('items__product')
        else:
            orders = Order.objects.filter(
                user=request.user
            ).prefetch_related('items__product')

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            if request.user.role in ['staff', 'admin']:
                order = Order.objects.prefetch_related(
                    'items__product'
                ).get(id=pk)
            else:
                order = Order.objects.prefetch_related(
                    'items__product'
                ).get(id=pk, user=request.user)

        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)

    @transaction.atomic
    def create(self, request):

        # Get saved address
        address_id = request.data.get('address_id')

        if not address_id:
            return Response(
                {'detail': 'Address ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            address = Address.objects.get(
                id=address_id,
                user=request.user
            )
        except Address.DoesNotExist:
            return Response(
                {'detail': 'Address not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Save address snapshot inside the order
        shipping_address = (
            f"{address.full_name}, "
            f"{address.address_line}, "
            f"{address.city}, "
            f"{address.state} - "
            f"{address.postal_code}, "
            f"Phone: {address.phone_number}"
        )

        # Get cart
        cart = Cart.objects.filter(
            user=request.user
        ).first()

        if not cart:
            return Response(
                {'detail': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = CartItem.objects.select_related(
            'product'
        ).filter(cart=cart)

        if not cart_items.exists():
            return Response(
                {'detail': 'Cart is empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_amount = Decimal('0.00')
        order_items_data = []

        # Check stock
        for cart_item in cart_items:

            inventory = Inventory.objects.select_for_update().get(
                product=cart_item.product
            )

            if cart_item.quantity > inventory.available_quantity:
                return Response(
                    {
                        'detail': (
                            f'Insufficient stock for '
                            f'{cart_item.product.name}. '
                            f'Only {inventory.available_quantity} available.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            price = cart_item.product.price
            subtotal = price * cart_item.quantity

            total_amount += subtotal

            order_items_data.append(
                {
                    'product': cart_item.product,
                    'quantity': cart_item.quantity,
                    'price': price,
                    'subtotal': subtotal,
                    'inventory': inventory
                }
            )

        # Create order
        order = Order.objects.create(
            user=request.user,
            order_number=f"SF-{uuid.uuid4().hex[:10].upper()}",
            total_amount=total_amount,
            shipping_address=shipping_address,
            status='pending',
            payment_status='pending'
        )

        # Create order items and reduce inventory
        for item in order_items_data:

            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
                subtotal=item['subtotal']
            )

            inventory = item['inventory']
            inventory.quantity -= item['quantity']
            inventory.save()

        # Clear cart
        cart_items.delete()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )

    @action(
        detail=True,
        methods=['post'],
        url_path='cancel'
    )
    @transaction.atomic
    def cancel(self, request, pk=None):

        try:
            order = Order.objects.select_for_update().get(
                id=pk,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != 'pending':
            return Response(
                {'detail': 'Only pending orders can be cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Restore inventory
        for item in order.items.all():

            inventory = Inventory.objects.select_for_update().get(
                product=item.product
            )

            inventory.quantity += item.quantity
            inventory.save()

        order.status = 'cancelled'
        order.save()

        serializer = OrderSerializer(order)

        return Response(
            {
                'message': 'Order cancelled successfully.',
                'order': serializer.data
            },
            status=status.HTTP_200_OK
        )

    @action(
        detail=True,
        methods=['patch'],
        url_path='status',
        permission_classes=[IsStaffOrAdmin]
    )
    def update_status(self, request, pk=None):

        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_status = order.status
        new_status = request.data.get('status')

        # Allowed next status
        status_flow = {
            'pending': 'confirmed',
            'confirmed': 'processing',
            'processing': 'shipped',
            'shipped': 'delivered',
        }

        # Already cancelled
        if current_status == 'cancelled':
            return Response(
                {'detail': 'Cancelled orders cannot be updated.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Already delivered
        if current_status == 'delivered':
            return Response(
                {'detail': 'Delivered orders cannot be updated.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validate requested status
        if new_status not in status_flow.values():
            return Response(
                {
                    'detail': (
                        'Invalid status. Allowed statuses are: '
                        'confirmed, processing, shipped, delivered.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check correct sequence
        expected_status = status_flow.get(current_status)

        if new_status != expected_status:
            return Response(
                {
                    'detail': (
                        f'Invalid status transition. '
                        f'{current_status} can only move to '
                        f'{expected_status}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save()

        serializer = OrderSerializer(order)

        return Response(serializer.data)


class MockPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):

        try:
            order = Order.objects.select_for_update().get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Order not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status == 'cancelled':
            return Response(
                {'detail': 'Cancelled orders cannot be paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.status == 'delivered':
            return Response(
                {'detail': 'Delivered orders cannot be paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if order.payment_status == 'paid':
            return Response(
                {'detail': 'Order is already paid.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        payment = Payment.objects.create(
            order=order,
            payment_method='mock',
            transaction_id=f"TXN-{uuid.uuid4().hex[:12].upper()}",
            amount=order.total_amount,
            status='success'
        )

        order.payment_status = 'paid'

        if order.status == 'pending':
            order.status = 'confirmed'

        order.save()

        return Response(
            {
                'message': 'Payment successful.',
                'payment': PaymentSerializer(payment).data,
                'order': OrderSerializer(order).data
            },
            status=status.HTTP_200_OK
        )