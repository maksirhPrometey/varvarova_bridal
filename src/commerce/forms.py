from django import forms

from src.commerce.models import Order
from src.commerce.np import np_warehouses, resolve_city, resolve_warehouse
from src.commerce.order_services import PAYMENT_BANK, PAYMENT_LIQPAY, liqpay_enabled
from src.content.selectors import active_salons


def _control(placeholder: str, input_type: str = 'text', extra: dict | None = None):
    attrs = {
        'class': 'form-control',
        'placeholder': ' ',
        **(extra or {}),
    }
    if input_type == 'email':
        return forms.EmailInput(attrs=attrs)
    if input_type == 'tel':
        attrs['type'] = 'tel'
        attrs['autocomplete'] = 'tel'
        return forms.TextInput(attrs=attrs)
    if input_type == 'textarea':
        return forms.Textarea(attrs={**attrs, 'rows': 3})
    return forms.TextInput(attrs=attrs)


class CheckoutForm(forms.Form):
    customer_name = forms.CharField(
        label='Імʼя',
        max_length=255,
        widget=_control('Імʼя', extra={'autocomplete': 'name'}),
    )
    customer_email = forms.EmailField(
        label='Email',
        widget=_control('Email', 'email', {'autocomplete': 'email'}),
    )
    customer_phone = forms.CharField(
        label='Телефон',
        max_length=32,
        widget=_control('Телефон', 'tel'),
    )
    comment = forms.CharField(
        label='Коментар',
        required=False,
        widget=_control('Коментар', 'textarea'),
    )
    shipping_method = forms.ChoiceField(
        label='Доставка',
        choices=Order.ShippingMethod.choices,
        widget=forms.RadioSelect,
    )
    payment_method = forms.ChoiceField(
        label='Оплата',
        widget=forms.RadioSelect,
    )
    salon_id = forms.ChoiceField(label='Салон', required=False)
    np_city_name = forms.CharField(
        label='Місто',
        required=False,
        max_length=255,
        widget=_control('Місто', extra={'autocomplete': 'off', 'data-np-city': 'true'}),
    )
    np_city_ref = forms.CharField(required=False, widget=forms.HiddenInput())
    np_warehouse_ref = forms.CharField(required=False)
    np_warehouse_name = forms.CharField(required=False, widget=forms.HiddenInput())
    shipping_address = forms.CharField(
        label='Адреса',
        required=False,
        widget=_control('Вулиця, будинок, квартира', 'textarea'),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        salons = [(str(salon.pk), f'{salon.name} — {salon.city}') for salon in active_salons()]
        self.fields['salon_id'].choices = [('', 'Оберіть салон')] + salons
        self.fields['salon_id'].widget.attrs['class'] = 'form-control'
        payments = [(PAYMENT_BANK, 'Оплата на рахунок')]
        if liqpay_enabled():
            payments.append((PAYMENT_LIQPAY, 'Картка (LiqPay)'))
        self.fields['payment_method'].choices = payments
        self.fields['np_warehouse_ref'].widget = forms.Select(
            attrs={'class': 'form-control', 'data-np-warehouse': 'true'}
        )
        city_ref = self.data.get('np_city_ref') or '' if self.is_bound else ''
        choices = [('', 'Оберіть відділення')]
        choices.extend((row['ref'], row['name']) for row in np_warehouses(city_ref))
        self.fields['np_warehouse_ref'].widget.choices = choices

    def clean_customer_phone(self):
        phone = self.cleaned_data['customer_phone'].strip()
        digits = ''.join(char for char in phone if char.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('Вкажіть телефон.')
        return phone

    def clean(self):
        cleaned = super().clean()
        method = cleaned.get('shipping_method')
        if method == Order.ShippingMethod.PICKUP_SALON:
            if not cleaned.get('salon_id'):
                self.add_error('salon_id', 'Оберіть салон.')
            return cleaned
        city = resolve_city(cleaned.get('np_city_ref') or '', cleaned.get('np_city_name') or '')
        if city is None:
            self.add_error('np_city_name', 'Оберіть місто з довідника.')
            return cleaned
        cleaned['np_city_ref'] = city['ref']
        cleaned['np_city_name'] = city['name']
        if method == Order.ShippingMethod.NP_WAREHOUSE:
            warehouse = resolve_warehouse(
                city['ref'],
                cleaned.get('np_warehouse_ref') or '',
                cleaned.get('np_warehouse_name') or '',
            )
            if warehouse is None:
                self.add_error('np_warehouse_ref', 'Оберіть відділення.')
            else:
                cleaned['np_warehouse_ref'] = warehouse['ref']
                cleaned['np_warehouse_name'] = warehouse['name']
        if method == Order.ShippingMethod.NP_COURIER and not (cleaned.get('shipping_address') or '').strip():
            self.add_error('shipping_address', 'Вкажіть адресу.')
        return cleaned
