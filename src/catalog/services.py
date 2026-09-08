from django.db import IntegrityError, transaction

from src.catalog.exceptions import WishlistError
from src.catalog.models import Product, WishlistItem
from src.catalog.selectors import active_products_by_ids, parse_wishlist_ids
from src.users.models import User


def wishlist_count_for(user: User) -> int:
    return WishlistItem.objects.filter(user=user).count()


@transaction.atomic
def toggle_wishlist(user: User, product_id: int) -> tuple[bool, int]:
    if product_id < 1:
        raise WishlistError('Некоректні дані.')
    product = Product.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        raise WishlistError('Товар недоступний.')
    existing = WishlistItem.objects.filter(user=user, product=product).first()
    if existing:
        existing.delete()
        return False, wishlist_count_for(user)
    try:
        WishlistItem.objects.create(user=user, product=product)
    except IntegrityError:
        return True, wishlist_count_for(user)
    return True, wishlist_count_for(user)


@transaction.atomic
def merge_ids_for_user(user: User, ids: list) -> int:
    for product in active_products_by_ids(parse_wishlist_ids(ids)):
        WishlistItem.objects.get_or_create(user=user, product=product)
    return wishlist_count_for(user)
