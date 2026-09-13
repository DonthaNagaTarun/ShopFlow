from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Inventory, Product

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart = Cart.objects.prefetch_related(
            'items__product'
        ).get(id=cart.id)

        serializer = CartSerializer(cart)

        return Response(serializer.data)

    def create(self, request):
        product_id = request.data.get('product')
        quantity = request.data.get('quantity')

        if not product_id:
            return Response(
                {'detail': 'Product ID is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not quantity:
            return Response(
                {'detail': 'Quantity is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'Quantity must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            return Response(
                {'detail': 'Quantity must be greater than 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True
            )
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            inventory = Inventory.objects.get(
                product=product
            )
        except Inventory.DoesNotExist:
            return Response(
                {'detail': 'Inventory not found for this product.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        existing_item = CartItem.objects.filter(
            cart=cart,
            product=product
        ).first()

        current_quantity = (
            existing_item.quantity
            if existing_item
            else 0
        )

        requested_quantity = current_quantity + quantity

        if requested_quantity > inventory.available_quantity:
            return Response(
                {
                    'detail': (
                        f'Only {inventory.available_quantity} '
                        f'{product.name} available.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if existing_item:
            existing_item.quantity = requested_quantity
            existing_item.save()

            serializer = CartItemSerializer(existing_item)

            return Response(
                {
                    'message': 'Cart item quantity updated.',
                    'item': serializer.data
                },
                status=status.HTTP_200_OK
            )

        cart_item = CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity
        )

        serializer = CartItemSerializer(cart_item)

        return Response(
            {
                'message': 'Product added to cart.',
                'item': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    def update(self, request, pk=None):
        try:
            cart_item = CartItem.objects.select_related(
                'product',
                'cart'
            ).get(
                id=pk,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        quantity = request.data.get('quantity')

        if quantity is None:
            return Response(
                {'detail': 'Quantity is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response(
                {'detail': 'Quantity must be a valid number.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            return Response(
                {'detail': 'Quantity must be greater than 0.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            inventory = Inventory.objects.get(
                product=cart_item.product
            )
        except Inventory.DoesNotExist:
            return Response(
                {'detail': 'Inventory not found.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity > inventory.available_quantity:
            return Response(
                {
                    'detail': (
                        f'Only {inventory.available_quantity} '
                        f'{cart_item.product.name} available.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = quantity
        cart_item.save()

        serializer = CartItemSerializer(cart_item)

        return Response(serializer.data)

    def destroy(self, request, pk=None):
        try:
            cart_item = CartItem.objects.get(
                id=pk,
                cart__user=request.user
            )
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Cart item not found.'},
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )