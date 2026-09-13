from django.contrib import admin

from .models import Category, Product
from .models import Category, Inventory, Product

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'is_active',
        'created_at',
    )

    list_filter = (
        'is_active',
    )

    search_fields = (
        'name',
    )


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'sku',
        'category',
        'price',
        'stock',
        'is_active',
        'created_at',
    )

    list_filter = (
        'category',
        'is_active',
    )

    search_fields = (
        'name',
        'sku',
    )

    list_editable = (
        'price',
        'stock',
        'is_active',
    )
    @admin.register(Inventory)
    class InventoryAdmin(admin.ModelAdmin):
        list_display = (
            'product',
            'quantity',
            'reserved_quantity',
            'available_quantity',
            'low_stock_threshold',
            'is_low_stock',
            'updated_at',
        )

        list_filter = (
            'low_stock_threshold',
        )

        search_fields = (
            'product__name',
            'product__sku',
        )

        readonly_fields = (
            'available_quantity',
            'is_low_stock',
        )