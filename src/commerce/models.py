from decimal import Decimal

from django.db import models
from django.db.models import Q

from src.core.models import CreatedAtModel, TimeStampedModel


class Cart(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'Активний'
        CONVERTED = 'converted', 'Оформлений'
        ABANDONED = 'abandoned', 'Покинутий'

    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='carts',
        verbose_name='Користувач',
    )
    session_key = models.CharField('Ключ сесії', max_length=40, null=True, blank=True)
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=Status.choices,
        default=Status.ACTIVE,
    )

    class Meta:
        db_table = 'commerce_cart'
        verbose_name = 'Кошик'
        verbose_name_plural = 'Кошики'
        indexes = [
            models.Index(fields=['session_key', 'status'], name='commerce_cart_session_status'),
            models.Index(fields=['user', 'status'], name='commerce_cart_user_status'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(user__isnull=False) | Q(session_key__isnull=False),
                name='commerce_cart_user_or_session',
            ),
            models.UniqueConstraint(
                fields=['user'],
                condition=Q(status='active') & Q(user__isnull=False),
                name='commerce_cart_one_active_per_user',
            ),
            models.UniqueConstraint(
                fields=['session_key'],
                condition=Q(status='active') & Q(session_key__isnull=False),
                name='commerce_cart_one_active_per_session',
            ),
        ]

    def __str__(self) -> str:
        return f'Cart {self.pk} ({self.status})'


class CartItem(TimeStampedModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Кошик',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.PROTECT,
        related_name='cart_items',
        verbose_name='Товар',
    )
    qty = models.PositiveIntegerField('Кількість', default=1)

    class Meta:
        db_table = 'commerce_cart_item'
        verbose_name = 'Позиція кошика'
        verbose_name_plural = 'Позиції кошика'
        constraints = [
            models.UniqueConstraint(
                fields=['cart', 'product'],
                name='commerce_cart_item_cart_product_uniq',
            ),
            models.CheckConstraint(
                condition=Q(qty__gte=1),
                name='commerce_cart_item_qty_gte_1',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.cart_id}:{self.product_id}×{self.qty}'


class Order(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = 'new', 'Нове'
        AWAITING_PAYMENT = 'awaiting_payment', 'Очікує оплату'
        PAID = 'paid', 'Оплачене'
        PROCESSING = 'processing', 'Обробка'
        SHIPPED = 'shipped', 'Відправлене'
        DONE = 'done', 'Виконане'
        CANCELLED = 'cancelled', 'Скасоване'

    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Очікує'
        PAID = 'paid', 'Оплачено'
        FAILED = 'failed', 'Помилка'
        REFUNDED = 'refunded', 'Повернення'

    class ShippingMethod(models.TextChoices):
        NP_WAREHOUSE = 'np_warehouse', 'НП відділення'
        NP_COURIER = 'np_courier', 'НП курʼєр'
        PICKUP_SALON = 'pickup_salon', 'Самовивіз із салону'

    number = models.CharField('Номер', max_length=32, unique=True)
    user = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name='Користувач',
    )
    status = models.CharField(
        'Статус',
        max_length=32,
        choices=Status.choices,
        default=Status.NEW,
    )
    customer_name = models.CharField('Імʼя', max_length=255)
    customer_email = models.EmailField('Email')
    customer_phone = models.CharField('Телефон', max_length=32)
    comment = models.TextField('Коментар', null=True, blank=True)
    subtotal_uah = models.DecimalField('Підсумок, грн', max_digits=12, decimal_places=2)
    shipping_uah = models.DecimalField(
        'Доставка, грн',
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
    )
    total_uah = models.DecimalField('Разом, грн', max_digits=12, decimal_places=2)
    payment_method = models.CharField('Спосіб оплати', max_length=32)
    payment_status = models.CharField(
        'Статус оплати',
        max_length=32,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
    )
    paid_at = models.DateTimeField('Оплачено', null=True, blank=True)
    shipping_method = models.CharField(
        'Спосіб доставки',
        max_length=32,
        choices=ShippingMethod.choices,
    )
    np_city_ref = models.CharField('НП city ref', max_length=64, null=True, blank=True)
    np_city_name = models.CharField('НП місто', max_length=255, null=True, blank=True)
    np_warehouse_ref = models.CharField('НП warehouse ref', max_length=64, null=True, blank=True)
    np_warehouse_name = models.CharField('НП відділення', max_length=255, null=True, blank=True)
    shipping_address = models.TextField('Адреса доставки', null=True, blank=True)
    pickup_salon_name = models.CharField('Салон', max_length=255, null=True, blank=True)
    pickup_salon_address = models.CharField(
        'Адреса салону',
        max_length=512,
        null=True,
        blank=True,
    )

    class Meta:
        db_table = 'commerce_order'
        verbose_name = 'Замовлення'
        verbose_name_plural = 'Замовлення'
        indexes = [
            models.Index(fields=['status'], name='commerce_order_status'),
            models.Index(fields=['payment_status'], name='commerce_order_pay_status'),
            models.Index(fields=['customer_email'], name='commerce_order_email'),
            models.Index(fields=['created_at'], name='commerce_order_created'),
        ]

    def __str__(self) -> str:
        return self.number


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Замовлення',
    )
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items',
        verbose_name='Товар',
    )
    sku_snapshot = models.CharField('SKU snapshot', max_length=64)
    name_snapshot = models.CharField('Назва snapshot', max_length=255)
    unit_price_uah = models.DecimalField('Ціна, грн', max_digits=12, decimal_places=2)
    qty = models.PositiveIntegerField('Кількість')
    line_total_uah = models.DecimalField('Сума рядка, грн', max_digits=12, decimal_places=2)

    class Meta:
        db_table = 'commerce_order_item'
        verbose_name = 'Позиція замовлення'
        verbose_name_plural = 'Позиції замовлення'
        constraints = [
            models.CheckConstraint(
                condition=Q(qty__gte=1),
                name='commerce_order_item_qty_gte_1',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.order_id}:{self.sku_snapshot}'


class OrderStatusLog(CreatedAtModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='status_logs',
        verbose_name='Замовлення',
    )
    from_status = models.CharField('Зі статусу', max_length=32, null=True, blank=True)
    to_status = models.CharField('До статусу', max_length=32)
    note = models.TextField('Нотатка', null=True, blank=True)
    actor = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_status_events',
        verbose_name='Автор',
    )

    class Meta:
        db_table = 'commerce_order_status_log'
        verbose_name = 'Лог статусу замовлення'
        verbose_name_plural = 'Логи статусів замовлень'
        ordering = ['created_at']

    def __str__(self) -> str:
        return f'{self.order_id}: {self.from_status} → {self.to_status}'
