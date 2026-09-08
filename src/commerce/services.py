from django.db import IntegrityError, transaction

from src.catalog.models import Product
from src.commerce.exceptions import CartError
from src.commerce.models import Cart, CartItem
from src.users.models import User


def _ensure_session_key(request) -> str | None:
    if request.user.is_authenticated:
        return request.session.session_key
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def get_active_cart(request) -> Cart:
    if request.user.is_authenticated:
        return _get_or_create_user_cart(request.user)
    return _get_or_create_session_cart(_ensure_session_key(request))


def peek_active_cart(request) -> Cart | None:
    if request.user.is_authenticated:
        return Cart.objects.filter(user=request.user, status=Cart.Status.ACTIVE).first()
    session_key = request.session.session_key
    if not session_key:
        return None
    return Cart.objects.filter(
        session_key=session_key,
        status=Cart.Status.ACTIVE,
        user__isnull=True,
    ).first()


def _get_or_create_user_cart(user: User) -> Cart:
    cart = Cart.objects.filter(user=user, status=Cart.Status.ACTIVE).first()
    if cart:
        return cart
    try:
        return Cart.objects.create(user=user, session_key=None, status=Cart.Status.ACTIVE)
    except IntegrityError:
        return Cart.objects.get(user=user, status=Cart.Status.ACTIVE)


def _get_or_create_session_cart(session_key: str) -> Cart:
    cart = Cart.objects.filter(
        session_key=session_key,
        status=Cart.Status.ACTIVE,
        user__isnull=True,
    ).first()
    if cart:
        return cart
    try:
        return Cart.objects.create(
            user=None,
            session_key=session_key,
            status=Cart.Status.ACTIVE,
        )
    except IntegrityError:
        return Cart.objects.get(
            session_key=session_key,
            status=Cart.Status.ACTIVE,
            user__isnull=True,
        )


def _require_qty(qty: int) -> int:
    if qty < 1:
        raise CartError('Кількість має бути не менше 1.')
    return qty


def add_item(request, *, product_id: int, qty: int = 1) -> CartItem:
    qty = _require_qty(qty)
    _ensure_session_key(request)
    with transaction.atomic():
        product = (
            Product.objects.select_for_update().filter(pk=product_id, is_active=True).first()
        )
        if product is None:
            raise CartError('Товар недоступний.')
        if product.stock_qty < 1:
            raise CartError('Наразі немає в наявності.')
        cart = Cart.objects.select_for_update().get(pk=get_active_cart(request).pk)
        item = cart.items.filter(product=product).first()
        new_qty = (item.qty if item else 0) + qty
        if new_qty > product.stock_qty:
            raise CartError('Недостатньо в наявності.')
        if item:
            item.qty = new_qty
            item.save(update_fields=['qty', 'updated_at'])
            return item
        try:
            return CartItem.objects.create(cart=cart, product=product, qty=qty)
        except IntegrityError:
            item = cart.items.filter(product=product).first()
            if item is None:
                raise CartError('Не вдалося додати товар.')
            new_qty = item.qty + qty
            if new_qty > product.stock_qty:
                raise CartError('Недостатньо в наявності.')
            item.qty = new_qty
            item.save(update_fields=['qty', 'updated_at'])
            return item


def update_qty(request, *, item_id: int, qty: int) -> CartItem:
    qty = _require_qty(qty)
    _ensure_session_key(request)
    with transaction.atomic():
        cart = Cart.objects.select_for_update().get(pk=get_active_cart(request).pk)
        item = (
            cart.items.select_for_update()
            .select_related('product')
            .filter(pk=item_id)
            .first()
        )
        if item is None:
            raise CartError('Позицію не знайдено.')
        if not item.product.is_active:
            raise CartError('Товар недоступний.')
        if qty > item.product.stock_qty:
            raise CartError('Недостатньо в наявності.')
        item.qty = qty
        item.save(update_fields=['qty', 'updated_at'])
        return item


def remove_item(request, *, item_id: int) -> None:
    _ensure_session_key(request)
    with transaction.atomic():
        cart = Cart.objects.select_for_update().get(pk=get_active_cart(request).pk)
        item = cart.items.filter(pk=item_id).first()
        if item is None:
            raise CartError('Позицію не знайдено.')
        item.delete()


@transaction.atomic
def merge_guest_cart(user: User, session_key: str | None) -> Cart | None:
    if user is None or not session_key:
        return (
            Cart.objects.filter(user=user, status=Cart.Status.ACTIVE).first()
            if user
            else None
        )
    guest = (
        Cart.objects.select_for_update()
        .filter(session_key=session_key, status=Cart.Status.ACTIVE, user__isnull=True)
        .first()
    )
    user_cart = (
        Cart.objects.select_for_update().filter(user=user, status=Cart.Status.ACTIVE).first()
    )
    if guest is None:
        return user_cart
    if user_cart is None:
        guest.user = user
        guest.session_key = None
        guest.save(update_fields=['user', 'session_key', 'updated_at'])
        return guest
    if guest.pk == user_cart.pk:
        return user_cart
    for item in list(guest.items.select_related('product')):
        _merge_line(user_cart, item)
    guest.status = Cart.Status.CONVERTED
    guest.save(update_fields=['status', 'updated_at'])
    return user_cart


def _merge_line(user_cart: Cart, item: CartItem) -> None:
    stock = item.product.stock_qty
    existing = user_cart.items.filter(product_id=item.product_id).first()
    if stock < 1:
        item.delete()
        if existing:
            existing.delete()
        return
    if existing:
        existing.qty = min(existing.qty + item.qty, stock)
        existing.save(update_fields=['qty', 'updated_at'])
        item.delete()
        return
    item.qty = min(item.qty, stock)
    item.cart = user_cart
    item.save(update_fields=['cart', 'qty', 'updated_at'])
