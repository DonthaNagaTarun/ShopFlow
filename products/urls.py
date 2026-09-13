from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    CategoryViewSet,
    ProductViewSet,
    InventoryViewSet,
    ReviewViewSet,
)


router = DefaultRouter()

router.register(
    'categories',
    CategoryViewSet,
    basename='categories'
)

router.register(
    'inventory',
    InventoryViewSet,
    basename='inventory'
)

router.register(
    'reviews',
    ReviewViewSet,
    basename='reviews'
)

router.register(
    '',
    ProductViewSet,
    basename='products'
)


urlpatterns = [
    path(
        '',
        include(router.urls)
    ),
]