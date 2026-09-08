from decimal import Decimal

from django.db.models import QuerySet, Sum

from src.commerce.models import Cart, CartItem, Order
from src.users.models import User


def orders_for_user(user: User) -> QuerySet[Order]:
    return (
        Order.objects.filter(user=user)
        .prefetch_related('items')
        .order_by('-created_at', '-id')
    )


def order_for_account(*, user: User, number: str) -> Order | None:
    queryset = Order.objects.prefetch_related('items').filter(number=number)
    if user.is_staff or user.is_superuser:
        return queryset.first()
    return queryset.filter(user=user).first()


def items_for_cart(cart: Cart) -> QuerySet[CartItem]:
    return (
        cart.items.select_related('product', 'product__category')
        .prefetch_related('product__images')
        .order_by('created_at', 'id')
    )


def cart_qty_sum(cart: Cart | None) -> int:
    if cart is None:
        return 0
    return cart.items.aggregate(total=Sum('qty'))['total'] or 0


def cart_display(cart: Cart | None) -> dict:
    if cart is None:
        return {'lines': [], 'subtotal': Decimal('0.00'), 'count': 0}
    lines = []
    subtotal = Decimal('0.00')
    count = 0
    for item in items_for_cart(cart):
        line_uah = item.product.price_uah * item.qty
        subtotal += line_uah
        count += item.qty
        lines.append(
            {
                'item': item,
                'unit_uah': item.product.price_uah,
                'line_uah': line_uah,
                'image': item.product.get_main_image(),
            }
        )
    return {'lines': lines, 'subtotal': subtotal, 'count': count}


def uk_positions_word(count: int) -> str:
    remainder = abs(count) % 100
    if 11 <= remainder <= 14:
        return 'позицій'
    last = remainder % 10
    if last == 1:
        return 'позиція'
    if 2 <= last <= 4:
        return 'позиції'
    return 'позицій'
