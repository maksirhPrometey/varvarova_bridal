from decimal import Decimal

from django.conf import settings
from django.core.mail import send_mail
from django.db import IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from src.catalog.models import Product
from src.commerce.exceptions import CheckoutError, OrderStatusError
from src.commerce.models import Order, OrderItem, OrderStatusLog
from src.commerce.np import resolve_city, resolve_warehouse
from src.commerce.services import peek_active_cart
from src.content.models import Salon
from src.users.models import User

ALLOWED_TRANSITIONS = {
    Order.Status.NEW: {Order.Status.AWAITING_PAYMENT, Order.Status.CANCELLED},
    Order.Status.AWAITING_PAYMENT: {Order.Status.PAID, Order.Status.CANCELLED},
    Order.Status.PAID: {Order.Status.PROCESSING, Order.Status.CANCELLED},
    Order.Status.PROCESSING: {Order.Status.SHIPPED, Order.Status.CANCELLED},
    Order.Status.SHIPPED: {Order.Status.DONE},
    Order.Status.DONE: set(),
    Order.Status.CANCELLED: set(),
}

PAYMENT_BANK = 'bank'
PAYMENT_LIQPAY = 'liqpay'


def liqpay_enabled() -> bool:
    return bool(
        getattr(settings, 'LIQPAY_PUBLIC_KEY', '')
        and getattr(settings, 'LIQPAY_PRIVATE_KEY', '')
    )


def allocate_order_number() -> str:
    day = timezone.localdate().strftime('%Y%m%d')
    prefix = f'VV-{day}-'
    last = (
        Order.objects.filter(number__startswith=prefix)
        .order_by('-number')
        .values_list('number', flat=True)
        .first()
    )
    seq = int(last.rsplit('-', 1)[-1]) + 1 if last else 1
    return f'{prefix}{seq:04d}'


def _can_manage_orders(user: User | None) -> bool:
    if user is None or not user.is_authenticated:
        return False
    if user.is_superuser or user.role == User.Role.ADMIN:
        return True
    return user.is_staff and user.role == User.Role.MANAGER


def change_order_status(
    order: Order,
    to: str,
    *,
    user: User | None = None,
    note: str = '',
    allow_system: bool = False,
) -> Order:
    if not allow_system and not _can_manage_orders(user):
        raise OrderStatusError('Немає прав змінювати статус.')
    allowed = ALLOWED_TRANSITIONS.get(order.status, set())
    if to not in allowed:
        raise OrderStatusError('Такий перехід статусу заборонений.')
    from_status = order.status
    restock = (
        to == Order.Status.CANCELLED
        and from_status in {Order.Status.PAID, Order.Status.PROCESSING}
    )
    order.status = to
    order.save(update_fields=['status', 'updated_at'])
    OrderStatusLog.objects.create(
        order=order,
        from_status=from_status,
        to_status=to,
        note=note or None,
        actor=user if user and user.is_authenticated else None,
    )
    if restock:
        for item in order.items.all():
            if item.product_id:
                Product.objects.filter(pk=item.product_id).update(
                    stock_qty=F('stock_qty') + item.qty
                )
    return order


def _shipping_snapshot(data: dict) -> dict:
    method = data['shipping_method']
    snapshot = {
        'shipping_method': method,
        'np_city_ref': None,
        'np_city_name': None,
        'np_warehouse_ref': None,
        'np_warehouse_name': None,
        'shipping_address': None,
        'pickup_salon_name': None,
        'pickup_salon_address': None,
    }
    if method == Order.ShippingMethod.NP_WAREHOUSE:
        city = resolve_city(data.get('np_city_ref') or '', data.get('np_city_name') or '')
        if city is None:
            raise CheckoutError('Оберіть місто Нової Пошти.')
        warehouse = resolve_warehouse(
            city['ref'],
            data.get('np_warehouse_ref') or '',
            data.get('np_warehouse_name') or '',
        )
        if warehouse is None:
            raise CheckoutError('Оберіть відділення Нової Пошти.')
        snapshot.update(
            {
                'np_city_ref': city['ref'],
                'np_city_name': city['name'],
                'np_warehouse_ref': warehouse['ref'],
                'np_warehouse_name': warehouse['name'],
            }
        )
        return snapshot
    if method == Order.ShippingMethod.NP_COURIER:
        city = resolve_city(data.get('np_city_ref') or '', data.get('np_city_name') or '')
        address = (data.get('shipping_address') or '').strip()
        if city is None or not address:
            raise CheckoutError('Вкажіть місто та адресу для курʼєра.')
        snapshot.update(
            {
                'np_city_ref': city['ref'],
                'np_city_name': city['name'],
                'shipping_address': address,
            }
        )
        return snapshot
    if method == Order.ShippingMethod.PICKUP_SALON:
        salon = Salon.objects.filter(pk=data.get('salon_id'), is_active=True).first()
        if salon is None:
            raise CheckoutError('Оберіть салон для самовивозу.')
        snapshot.update(
            {
                'pickup_salon_name': salon.name,
                'pickup_salon_address': f'{salon.city}, {salon.address}',
            }
        )
        return snapshot
    raise CheckoutError('Оберіть спосіб доставки.')


def _notify_customer(order: Order) -> None:
    if not order.customer_email:
        return
    send_mail(
        f'Замовлення {order.number} — Varvarova',
        (
            f'Дякуємо, {order.customer_name}.\n'
            f'Номер замовлення: {order.number}\n'
            f'Сума: {order.total_uah} грн\n'
        ),
        settings.DEFAULT_FROM_EMAIL,
        [order.customer_email],
        fail_silently=True,
    )


def place_order(request, data: dict) -> Order:
    payment = data['payment_method']
    if payment not in {PAYMENT_BANK, PAYMENT_LIQPAY}:
        raise CheckoutError('Оберіть спосіб оплати.')
    if payment == PAYMENT_LIQPAY and not liqpay_enabled():
        raise CheckoutError('Оплата карткою тимчасово недоступна.')
    shipping = _shipping_snapshot(data)
    with transaction.atomic():
        cart = peek_active_cart(request)
        if cart is None:
            raise CheckoutError('Кошик порожній.')
        items = list(cart.items.select_related('product').select_for_update())
        if not items:
            raise CheckoutError('Кошик порожній.')
        product_ids = [item.product_id for item in items]
        locked = {
            product.pk: product
            for product in Product.objects.select_for_update().filter(pk__in=product_ids)
        }
        lines = []
        subtotal = Decimal('0.00')
        for item in items:
            product = locked.get(item.product_id)
            if product is None or not product.is_active:
                raise CheckoutError('Товар недоступний.')
            if product.stock_qty < item.qty:
                raise CheckoutError('Недостатньо в наявності.')
            unit = product.price_uah
            line_total = unit * item.qty
            subtotal += line_total
            lines.append((item, product, unit, line_total))
        shipping_uah = Decimal('0.00')
        user = request.user if request.user.is_authenticated else None
        order = None
        for _attempt in range(5):
            try:
                order = Order.objects.create(
                    number=allocate_order_number(),
                    user=user,
                    customer_name=data['customer_name'].strip(),
                    customer_email=data['customer_email'].strip().lower(),
                    customer_phone=data['customer_phone'].strip(),
                    comment=(data.get('comment') or '').strip() or None,
                    subtotal_uah=subtotal,
                    shipping_uah=shipping_uah,
                    total_uah=subtotal + shipping_uah,
                    payment_method=payment,
                    payment_status=Order.PaymentStatus.PENDING,
                    **shipping,
                )
                break
            except IntegrityError:
                order = None
        if order is None:
            raise CheckoutError('Не вдалося створити замовлення. Спробуйте ще раз.')
        for item, product, unit, line_total in lines:
            OrderItem.objects.create(
                order=order,
                product=product,
                sku_snapshot=product.sku,
                name_snapshot=product.name,
                unit_price_uah=unit,
                qty=item.qty,
                line_total_uah=line_total,
            )
            updated = Product.objects.filter(pk=product.pk, stock_qty__gte=item.qty).update(
                stock_qty=F('stock_qty') - item.qty
            )
            if updated == 0:
                raise CheckoutError('Недостатньо в наявності.')
        cart.status = cart.Status.CONVERTED
        cart.save(update_fields=['status', 'updated_at'])
        OrderStatusLog.objects.create(
            order=order,
            from_status=None,
            to_status=Order.Status.NEW,
            note='Оформлення',
        )
        if payment == PAYMENT_LIQPAY:
            change_order_status(
                order,
                Order.Status.AWAITING_PAYMENT,
                allow_system=True,
                note='LiqPay',
            )
    request.session['last_order_id'] = order.pk
    request.session['last_order_number'] = order.number
    request.session.modified = True
    _notify_customer(order)
    return order
