import json

from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView

from src.catalog.exceptions import WishlistError
from src.catalog.selectors import (
    active_products_by_ids,
    grid_cols_for,
    parse_wishlist_ids,
    wishlist_products_for_user,
)
from src.catalog.services import merge_ids_for_user, toggle_wishlist


def _json_body(request) -> dict:
    try:
        payload = json.loads(request.body or b'{}')
    except json.JSONDecodeError as exc:
        raise WishlistError('Некоректні дані.') from exc
    if not isinstance(payload, dict):
        raise WishlistError('Некоректні дані.')
    return payload


class WishlistView(TemplateView):
    template_name = 'catalog/wishlist.html'

    def get_context_data(self, **kwargs):
        if self.request.user.is_authenticated:
            products = wishlist_products_for_user(self.request.user)
        else:
            products = active_products_by_ids(parse_wishlist_ids(self.request.GET.get('ids')))
        context = super().get_context_data(**kwargs)
        context.update(
            {
                'products': products,
                'grid_cols': grid_cols_for(len(products)),
                'page_title': 'Улюблене',
            }
        )
        return context


class WishlistToggleView(View):
    http_method_names = ['post']

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Потрібен вхід.'}, status=401)
        try:
            product_id = int(_json_body(request).get('product_id'))
            in_wishlist, count = toggle_wishlist(request.user, product_id)
        except (TypeError, ValueError) as exc:
            return JsonResponse({'error': 'Некоректні дані.'}, status=400)
        except WishlistError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse({'in_wishlist': in_wishlist, 'count': count})


class WishlistMergeView(View):
    http_method_names = ['post']

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Потрібен вхід.'}, status=401)
        try:
            ids = _json_body(request).get('ids', [])
            if not isinstance(ids, list):
                raise WishlistError('Некоректні дані.')
            count = merge_ids_for_user(request.user, ids)
        except WishlistError as exc:
            return JsonResponse({'error': str(exc)}, status=400)
        return JsonResponse({'count': count})
