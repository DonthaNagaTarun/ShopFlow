from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import OrderViewSet, MockPaymentView


router = DefaultRouter()

router.register(
    'orders',
    OrderViewSet,
    basename='orders'
)


urlpatterns = [
    path(
        '',
        include(router.urls)
    ),

    path(
        'payments/<int:order_id>/pay/',
        MockPaymentView.as_view(),
        name='mock-payment'
    ),
]