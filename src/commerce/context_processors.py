from src.commerce.selectors import cart_qty_sum
from src.commerce.services import peek_active_cart


def cart(request):
    return {'cart_count': cart_qty_sum(peek_active_cart(request))}
