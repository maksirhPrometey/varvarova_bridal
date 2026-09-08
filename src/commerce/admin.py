from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from src.commerce.models import Cart, CartItem, Order, OrderItem, OrderStatusLog


class CartItemInline(TabularInline):
    model = CartItem
    extra = 0
    autocomplete_fields = ('product',)


class OrderItemInline(TabularInline):
    model = OrderItem
    extra = 0
    autocomplete_fields = ('product',)


class OrderStatusLogInline(TabularInline):
    model = OrderStatusLog
    extra = 0
    readonly_fields = ('from_status', 'to_status', 'note', 'actor', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Cart)
class CartAdmin(ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'status_badge', 'updated_at')
    list_filter = ('status',)
    search_fields = ('session_key', 'user__email')
    autocomplete_fields = ('user',)
    inlines = (CartItemInline,)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    @display(
        description='Статус',
        label={
            Cart.Status.ACTIVE: 'info',
            Cart.Status.CONVERTED: 'success',
            Cart.Status.ABANDONED: 'danger',
        },
    )
    def status_badge(self, obj: Cart):
        return obj.status


@admin.register(Order)
class OrderAdmin(ModelAdmin):
    list_display = (
        'number',
        'customer_name',
        'customer_email',
        'status_badge',
        'payment_badge',
        'total_uah',
        'created_at',
    )
    list_filter = ('status', 'payment_status', 'shipping_method')
    search_fields = ('number', 'customer_email', 'customer_phone', 'customer_name')
    autocomplete_fields = ('user',)
    inlines = (OrderItemInline, OrderStatusLogInline)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    def get_readonly_fields(self, request, obj=None):
        fields = list(self.readonly_fields)
        if obj:
            fields.extend(['number', 'subtotal_uah', 'shipping_uah', 'total_uah'])
        return fields

    @display(
        description='Статус',
        label={
            Order.Status.NEW: 'info',
            Order.Status.AWAITING_PAYMENT: 'warning',
            Order.Status.PAID: 'success',
            Order.Status.PROCESSING: 'info',
            Order.Status.SHIPPED: 'info',
            Order.Status.DONE: 'success',
            Order.Status.CANCELLED: 'danger',
        },
    )
    def status_badge(self, obj: Order):
        return obj.status

    @display(
        description='Оплата',
        label={
            Order.PaymentStatus.PENDING: 'warning',
            Order.PaymentStatus.PAID: 'success',
            Order.PaymentStatus.FAILED: 'danger',
            Order.PaymentStatus.REFUNDED: 'info',
        },
    )
    def payment_badge(self, obj: Order):
        return obj.payment_status
