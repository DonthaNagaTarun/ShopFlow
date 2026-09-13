from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Category, Inventory, Product,Review
from .permissions import IsAdmin, IsStaffOrAdmin
from .serializers import (
    CategorySerializer,
    InventorySerializer,
    ProductSerializer,
    ReviewSerializer,
)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]

        if self.action in ['create', 'update', 'partial_update']:
            return [IsStaffOrAdmin()]

        return [IsAuthenticated()]


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

    filterset_fields = ['category', 'is_active']
    search_fields = ['name', 'sku', 'description']
    ordering_fields = ['name', 'price', 'created_at', 'stock']

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]

        if self.action in ['create', 'update', 'partial_update']:
            return [IsStaffOrAdmin()]

        return [IsAuthenticated()]


class InventoryViewSet(viewsets.ModelViewSet):
    queryset = Inventory.objects.select_related('product').all()
    serializer_class = InventorySerializer

    def get_permissions(self):
        if self.action == 'destroy':
            return [IsAdmin()]

        if self.action in ['create', 'update', 'partial_update']:
            return [IsStaffOrAdmin()]

        return [IsAuthenticated()]

# =======================================================
# REVIEW VIEWSET
# =======================================================

class ReviewViewSet(viewsets.ModelViewSet):

    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        return Review.objects.select_related(
            'product',
            'user'
        ).all()

    # ---------------------------------------------------
    # CREATE REVIEW
    # ---------------------------------------------------

    def perform_create(self, serializer):

        product = serializer.validated_data['product']

        # Same user cannot review same product twice
        if Review.objects.filter(
            product=product,
            user=self.request.user
        ).exists():

            raise serializers.ValidationError(
                'You have already reviewed this product.'
            )

        serializer.save(
            user=self.request.user
        )

    # ---------------------------------------------------
    # UPDATE REVIEW
    # ---------------------------------------------------

    def update(self, request, *args, **kwargs):

        review = self.get_object()

        if review.user != request.user:

            return Response(
                {
                    'detail': (
                        'You can only update your own review.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return super().update(
            request,
            *args,
            **kwargs
        )

    # ---------------------------------------------------
    # DELETE REVIEW
    # ---------------------------------------------------

    def destroy(self, request, *args, **kwargs):

        review = self.get_object()

        if review.user != request.user:

            return Response(
                {
                    'detail': (
                        'You can only delete your own review.'
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        review.delete()

        return Response(
            {
                'message': 'Review deleted successfully.'
            },
            status=status.HTTP_204_NO_CONTENT
        )