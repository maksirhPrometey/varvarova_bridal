from src.catalog.selectors import wishlist_product_ids_for_user
from src.catalog.services import wishlist_count_for


def wishlist(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return {'wishlist_count': 0, 'wishlist_ids': []}
    return {
        'wishlist_count': wishlist_count_for(request.user),
        'wishlist_ids': wishlist_product_ids_for_user(request.user),
    }
