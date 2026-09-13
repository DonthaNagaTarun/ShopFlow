from django.db import transaction
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from .models import Address
from .serializers import AddressSerializer


class AddressViewSet(viewsets.ModelViewSet):
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

    @transaction.atomic
    def perform_create(self, serializer):
        user = self.request.user
        address = serializer.save(user=user)

        # First address automatically becomes default
        has_other_address = Address.objects.filter(
            user=user
        ).exclude(pk=address.pk).exists()

        if address.is_default or not has_other_address:
            Address.objects.filter(
                user=user
            ).exclude(pk=address.pk).update(is_default=False)

            if not address.is_default:
                address.is_default = True
                address.save(update_fields=['is_default', 'updated_at'])

    @transaction.atomic
    def perform_update(self, serializer):
        address = serializer.save()

        # Only one default address allowed
        if address.is_default:
            Address.objects.filter(
                user=self.request.user
            ).exclude(pk=address.pk).update(is_default=False)

    @transaction.atomic
    def perform_destroy(self, instance):
        was_default = instance.is_default
        user = instance.user

        instance.delete()

        # If default address is deleted, promote another address
        if was_default:
            next_address = Address.objects.filter(
                user=user
            ).order_by('-created_at').first()

            if next_address:
                next_address.is_default = True
                next_address.save(
                    update_fields=['is_default', 'updated_at']
                )