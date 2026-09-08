from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from src.catalog.models import (
    Attribute,
    AttributeValue,
    Category,
    Product,
    ProductAttributeValue,
    ProductImage,
    WishlistItem,
)
from src.core.admin import TinyMCEAdminMixin


class AttributeValueInline(TabularInline):
    model = AttributeValue
    extra = 1


class ProductImageInline(TabularInline):
    model = ProductImage
    extra = 1


class ProductAttributeValueInline(TabularInline):
    model = ProductAttributeValue
    extra = 1
    autocomplete_fields = ('attribute_value',)


@admin.register(Category)
class CategoryAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('description',)
    list_display = ('name', 'slug', 'parent', 'is_active', 'sort_order')
    list_filter = ('is_active', 'parent')
    search_fields = ('name', 'slug')
    list_editable = ('is_active', 'sort_order')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('parent',)
    ordering = ('sort_order', 'name')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')


@admin.register(Attribute)
class AttributeAdmin(ModelAdmin):
    list_display = ('name', 'code', 'filterable', 'sort_order')
    list_editable = ('filterable', 'sort_order')
    search_fields = ('name', 'code')
    inlines = (AttributeValueInline,)
    ordering = ('sort_order', 'id')


@admin.register(AttributeValue)
class AttributeValueAdmin(ModelAdmin):
    list_display = ('value', 'attribute', 'slug', 'sort_order')
    list_filter = ('attribute',)
    search_fields = ('value', 'slug', 'attribute__name')
    autocomplete_fields = ('attribute',)
    ordering = ('attribute', 'sort_order', 'id')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('attribute')


@admin.register(Product)
class ProductAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('description',)
    list_display = (
        'main_photo',
        'name',
        'sku',
        'category',
        'price_uah',
        'stock_qty',
        'is_active',
        'is_featured',
    )
    list_display_links = ('main_photo', 'name')
    list_filter = ('is_active', 'is_featured', 'category')
    search_fields = ('name', 'sku', 'slug')
    list_editable = ('is_active', 'is_featured')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('category',)
    inlines = (ProductImageInline, ProductAttributeValueInline)
    ordering = ('sort_order', 'name')

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related('category')
            .prefetch_related('images')
        )

    @display(description='Фото', image=True)
    def main_photo(self, obj: Product):
        main = None
        first = None
        for image in obj.images.all():
            if first is None:
                first = image
            if image.is_main:
                main = image
                break
        chosen = main or first
        return chosen.image.url if chosen and chosen.image else None


@admin.register(WishlistItem)
class WishlistItemAdmin(ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__email', 'product__name', 'product__sku')
    autocomplete_fields = ('user', 'product')
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'product')
