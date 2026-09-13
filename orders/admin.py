from django.contrib import admin

from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = (
        'product',
        'quantity',
        'price',
        'subtotal',
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_number',
        'user',
        'status',
        'payment_status',
        'total_amount',
        'created_at',
    )

    list_filter = (
        'status',
        'payment_status',
        'created_at',
    )

    search_fields = (
        'order_number',
        'user__email',
    )

    readonly_fields = (
        'order_number',
        'total_amount',
        'created_at',
        'updated_at',
    )

    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product',
        'quantity',
        'price',
        'subtotal',
    )

    search_fields = (
        'order__order_number',
        'product__name',
    )