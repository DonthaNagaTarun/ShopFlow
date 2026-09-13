from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product

from .models import WishlistItem
from .serializers import WishlistItemSerializer


class WishlistViewSet(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    # ---------------------------------------------------
    # LIST WISHLIST
    # ---------------------------------------------------

    def list(self, request):

        wishlist = WishlistItem.objects.filter(
            user=request.user
        ).select_related('product')

        serializer = WishlistItemSerializer(
            wishlist,
            many=True
        )

        return Response(serializer.data)

    # ---------------------------------------------------
    # ADD PRODUCT TO WISHLIST
    # ---------------------------------------------------

    def create(self, request):

        product_id = request.data.get('product')

        if not product_id:
            return Response(
                {
                    'detail': 'Product ID is required.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            product = Product.objects.get(
                id=product_id,
                is_active=True
            )

        except Product.DoesNotExist:
            return Response(
                {
                    'detail': 'Product not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist_item, created = WishlistItem.objects.get_or_create(
            user=request.user,
            product=product
        )

        if not created:
            return Response(
                {
                    'detail': 'Product is already in your wishlist.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = WishlistItemSerializer(
            wishlist_item
        )

        return Response(
            {
                'message': 'Product added to wishlist.',
                'wishlist_item': serializer.data
            },
            status=status.HTTP_201_CREATED
        )

    # ---------------------------------------------------
    # REMOVE PRODUCT FROM WISHLIST
    # ---------------------------------------------------

    def destroy(self, request, pk=None):

        try:
            wishlist_item = WishlistItem.objects.get(
                id=pk,
                user=request.user
            )

        except WishlistItem.DoesNotExist:
            return Response(
                {
                    'detail': 'Wishlist item not found.'
                },
                status=status.HTTP_404_NOT_FOUND
            )

        wishlist_item.delete()

        return Response(
            {
                'message': 'Product removed from wishlist.'
            },
            status=status.HTTP_204_NO_CONTENT
        )