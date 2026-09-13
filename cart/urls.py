from django.urls import path

from .views import CartViewSet


cart_list = CartViewSet.as_view({
    'get': 'list',
    'post': 'create',
})

cart_detail = CartViewSet.as_view({
    'put': 'update',
    'patch': 'update',
    'delete': 'destroy',
})


urlpatterns = [
    path('cart/', cart_list, name='cart-list'),
    path('cart/<int:pk>/', cart_detail, name='cart-detail'),
]