from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views import View

from src.catalog.models import Product
from src.commerce.exceptions import CartError
from src.commerce.selectors import cart_display, cart_qty_sum, uk_positions_word
from src.commerce.services import (
    add_item,
    peek_active_cart,
    remove_item,
    update_qty,
)


def _post_int(request, name: str, default: int | None = None) -> int:
    raw = request.POST.get(name)
    if raw in (None, ''):
        if default is not None:
            return default
        raise CartError('Некоректні дані.')
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise CartError('Некоректні дані.') from exc


def _cart_context(request, *, error: str | None = None) -> dict:
    cart = peek_active_cart(request)
    display = cart_display(cart)
    count = display['count']
    return {
        'cart': cart,
        'lines': display['lines'],
        'subtotal': display['subtotal'],
        'cart_count': count,
        'positions_label': f'{count} {uk_positions_word(count)}' if count else 'Порожньо',
        'cart_error': error,
        'page_title': 'Кошик',
    }


def _cart_body(request, *, error: str | None = None):
    context = _cart_context(request, error=error)
    context['swap_count'] = True
    return render(request, 'commerce/partials/_cart_body.html', context)


class CartDetailView(View):
    def get(self, request):
        return render(request, 'commerce/cart.html', _cart_context(request))


class CartAddView(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            product_id = _post_int(request, 'product_id')
            qty = _post_int(request, 'qty', default=1)
            add_item(request, product_id=product_id, qty=qty)
        except CartError as exc:
            return _add_error(request, exc)
        if request.htmx:
            return _add_partial(request, product_id=int(request.POST['product_id']), added=True)
        return redirect('commerce:cart')


class CartQtyView(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            item_id = _post_int(request, 'item_id')
            if 'qty' in request.POST and request.POST.get('qty') not in (None, ''):
                qty = _post_int(request, 'qty')
            else:
                cart = peek_active_cart(request)
                current = cart.items.filter(pk=item_id).first() if cart else None
                if current is None:
                    raise CartError('Позицію не знайдено.')
                qty = current.qty + _post_int(request, 'delta')
            update_qty(request, item_id=item_id, qty=qty)
        except CartError as exc:
            if request.htmx:
                return _cart_body(request, error=str(exc))
            return HttpResponse(str(exc), status=400, content_type='text/plain; charset=utf-8')
        if request.htmx:
            return _cart_body(request)
        return redirect('commerce:cart')


class CartRemoveView(View):
    http_method_names = ['post']

    def post(self, request):
        try:
            remove_item(request, item_id=_post_int(request, 'item_id'))
        except CartError as exc:
            if request.htmx:
                return _cart_body(request, error=str(exc))
            return HttpResponse(str(exc), status=400, content_type='text/plain; charset=utf-8')
        if request.htmx:
            return _cart_body(request)
        return redirect('commerce:cart')


def _add_error(request, exc: CartError):
    raw_id = request.POST.get('product_id')
    try:
        product_id = int(raw_id)
    except (TypeError, ValueError):
        product_id = None
    if request.htmx and product_id:
        return _add_partial(request, product_id=product_id, added=False, error=str(exc))
    return HttpResponse(str(exc), status=400, content_type='text/plain; charset=utf-8')


def _add_partial(request, *, product_id: int, added: bool, error: str | None = None):
    product = Product.objects.filter(pk=product_id, is_active=True).first()
    if product is None:
        return HttpResponse('Товар недоступний.', status=400, content_type='text/plain; charset=utf-8')
    return render(
        request,
        'catalog/partials/pdp_cart_add_response.html',
        {
            'product': product,
            'cart_added': added,
            'cart_error': error,
            'cart_count': cart_qty_sum(peek_active_cart(request)),
        },
    )
