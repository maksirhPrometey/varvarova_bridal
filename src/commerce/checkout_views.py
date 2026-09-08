from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.views import View

from src.commerce.exceptions import CheckoutError
from src.commerce.forms import CheckoutForm
from src.commerce.models import Order
from src.commerce.np import np_cities, np_warehouses
from src.commerce.order_services import PAYMENT_BANK, place_order
from src.commerce.selectors import cart_display
from src.commerce.services import peek_active_cart
from src.content.selectors import active_salons, site_settings


def _checkout_context(request, form: CheckoutForm) -> dict:
    cart = peek_active_cart(request)
    display = cart_display(cart)
    return {
        'form': form,
        'lines': display['lines'],
        'subtotal': display['subtotal'],
        'page_title': 'Оформлення',
        'np_cities_url': '/api/np/cities/',
        'np_warehouses_url': '/api/np/warehouses/',
    }


class CheckoutView(View):
    def get(self, request):
        cart = peek_active_cart(request)
        if cart is None or not cart.items.exists():
            return redirect('commerce:cart')
        initial = {'payment_method': PAYMENT_BANK}
        if active_salons().exists():
            initial['shipping_method'] = Order.ShippingMethod.PICKUP_SALON
        if request.user.is_authenticated:
            user = request.user
            initial.update(
                {
                    'customer_name': user.get_full_name() or user.first_name,
                    'customer_email': user.email,
                    'customer_phone': user.phone or '',
                }
            )
        form = CheckoutForm(initial=initial)
        return render(request, 'commerce/checkout.html', _checkout_context(request, form))

    def post(self, request):
        cart = peek_active_cart(request)
        if cart is None or not cart.items.exists():
            return redirect('commerce:cart')
        form = CheckoutForm(request.POST)
        if not form.is_valid():
            return render(request, 'commerce/checkout.html', _checkout_context(request, form))
        try:
            place_order(request, form.cleaned_data)
        except CheckoutError as exc:
            form.add_error(None, str(exc))
            return render(request, 'commerce/checkout.html', _checkout_context(request, form))
        return redirect('commerce:checkout_thanks')


class CheckoutThanksView(View):
    def get(self, request):
        order_id = request.session.get('last_order_id')
        number = request.session.get('last_order_number')
        if not order_id or not number:
            raise Http404
        order = (
            Order.objects.prefetch_related('items')
            .filter(pk=order_id, number=number)
            .first()
        )
        if order is None:
            raise Http404
        contacts = site_settings().contacts_json or {}
        return render(
            request,
            'commerce/thanks.html',
            {
                'order': order,
                'page_title': 'Дякуємо',
                'bank': contacts.get('bank') or {},
                'contacts': contacts,
            },
        )


class NpCitiesView(View):
    def get(self, request):
        return JsonResponse({'results': np_cities(request.GET.get('q', ''))})


class NpWarehousesView(View):
    def get(self, request):
        return JsonResponse({'results': np_warehouses(request.GET.get('city', ''))})
