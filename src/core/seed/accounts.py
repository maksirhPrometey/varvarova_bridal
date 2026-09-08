from decimal import Decimal
from os import getenv

from django.utils import timezone

from src.catalog.models import Product, WishlistItem
from src.commerce.models import Order, OrderItem, OrderStatusLog
from src.users.models import User

ADMIN_EMAIL = 'admin@varvarova.com'
CUSTOMER_EMAIL = 'olena@example.com'
ADMIN_PASSWORD = getenv('SEED_ADMIN_PASSWORD', 'DemoAdmin123!')
CUSTOMER_PASSWORD = getenv('SEED_CUSTOMER_PASSWORD', 'DemoBride123!')


def _user(*, email: str, password: str, **fields) -> tuple[User, bool]:
    user = User.objects.filter(email=email).first()
    if user:
        for key, value in fields.items():
            setattr(user, key, value)
        user.set_password(password)
        user.save()
        return user, False
    if fields.get('is_superuser'):
        user = User.objects.create_superuser(email=email, password=password, **fields)
    else:
        user = User.objects.create_user(email=email, password=password, **fields)
    return user, True


def seed_accounts() -> dict[str, str]:
    admin, _ = _user(
        email=ADMIN_EMAIL,
        password=ADMIN_PASSWORD,
        first_name='Оксана',
        last_name='Варварова',
        phone='+380322000100',
        is_staff=True,
        is_superuser=True,
        role=User.Role.ADMIN,
    )
    customer, _ = _user(
        email=CUSTOMER_EMAIL,
        password=CUSTOMER_PASSWORD,
        first_name='Олена',
        last_name='Коваль',
        phone='+380671112233',
        role=User.Role.CUSTOMER,
    )

    featured = list(Product.objects.filter(is_active=True).order_by('sort_order')[:6])
    if len(featured) >= 2:
        WishlistItem.objects.get_or_create(user=customer, product=featured[0])
        WishlistItem.objects.get_or_create(user=customer, product=featured[1])

    if featured:
        _seed_orders(customer, featured)

    return {
        'admin_email': admin.email,
        'admin_password': ADMIN_PASSWORD,
        'customer_email': customer.email,
        'customer_password': CUSTOMER_PASSWORD,
    }


def _seed_orders(customer: User, products: list[Product]) -> None:
    first = products[0]
    second = products[1] if len(products) > 1 else products[0]
    third = products[2] if len(products) > 2 else products[0]
    paid_at = timezone.now()

    specs = [
        (
            'VV-1001',
            {
                'user': customer,
                'status': Order.Status.PROCESSING,
                'customer_name': 'Олена Коваль',
                'customer_email': customer.email,
                'customer_phone': customer.phone or '+380671112233',
                'subtotal_uah': first.price_uah,
                'shipping_uah': Decimal('0.00'),
                'total_uah': first.price_uah,
                'payment_method': 'liqpay',
                'payment_status': Order.PaymentStatus.PAID,
                'paid_at': paid_at,
                'shipping_method': Order.ShippingMethod.PICKUP_SALON,
                'pickup_salon_name': 'Varvarova Atelier',
                'pickup_salon_address': 'Львів, вул. Січових Стрільців, 12',
                'items': [(first, 1)],
                'log': (None, Order.Status.PROCESSING, 'Демо: в пошиві після примірки'),
            },
        ),
        (
            'VV-1002',
            {
                'user': customer,
                'status': Order.Status.AWAITING_PAYMENT,
                'customer_name': 'Олена Коваль',
                'customer_email': customer.email,
                'customer_phone': customer.phone or '+380671112233',
                'subtotal_uah': second.price_uah,
                'shipping_uah': Decimal('120.00'),
                'total_uah': second.price_uah + Decimal('120.00'),
                'payment_method': 'liqpay',
                'payment_status': Order.PaymentStatus.PENDING,
                'shipping_method': Order.ShippingMethod.NP_WAREHOUSE,
                'np_city_name': 'Київ',
                'np_warehouse_name': 'Відділення №12',
                'items': [(second, 1)],
                'log': (None, Order.Status.AWAITING_PAYMENT, 'Демо: очікує оплату'),
            },
        ),
        (
            'VV-1003',
            {
                'user': customer,
                'status': Order.Status.DONE,
                'customer_name': 'Олена Коваль',
                'customer_email': customer.email,
                'customer_phone': customer.phone or '+380671112233',
                'subtotal_uah': third.price_uah,
                'shipping_uah': Decimal('250.00'),
                'total_uah': third.price_uah + Decimal('250.00'),
                'payment_method': 'cod',
                'payment_status': Order.PaymentStatus.PAID,
                'paid_at': paid_at,
                'shipping_method': Order.ShippingMethod.NP_COURIER,
                'np_city_name': 'Львів',
                'shipping_address': 'вул. Личаківська, 15, кв. 8',
                'items': [(third, 1)],
                'log': (Order.Status.SHIPPED, Order.Status.DONE, 'Демо: видано'),
            },
        ),
    ]

    for number, payload in specs:
        items = payload.pop('items')
        log = payload.pop('log')
        order, created = Order.objects.get_or_create(number=number, defaults=payload)
        if not created:
            continue
        for product, qty in items:
            OrderItem.objects.create(
                order=order,
                product=product,
                sku_snapshot=product.sku,
                name_snapshot=product.name,
                unit_price_uah=product.price_uah,
                qty=qty,
                line_total_uah=product.price_uah * qty,
            )
        OrderStatusLog.objects.create(
            order=order,
            from_status=log[0],
            to_status=log[1],
            note=log[2],
            actor=customer,
        )
