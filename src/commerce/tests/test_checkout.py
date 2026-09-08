from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from src.catalog.models import Category, Product
from src.commerce.models import Cart, CartItem, Order, OrderItem
from src.content.models import Salon
from src.users.models import User


class CheckoutTests(TestCase):
    def setUp(self):
        category = Category.objects.create(name='Весільні', slug='wedding-chk')
        self.product = Product.objects.create(
            category=category,
            sku='CHK-1',
            slug='checkout-dress',
            name='Checkout',
            price_uah=Decimal('15000.00'),
            stock_qty=2,
        )
        self.salon = Salon.objects.create(
            name='Atelier Test',
            city='Львів',
            address='вул. Тестова, 1',
            is_active=True,
        )
        self.checkout_url = reverse('commerce:checkout')
        self.thanks_url = reverse('commerce:checkout_thanks')
        self.add_url = reverse('commerce:cart_add')

    def _fill_cart(self, qty=1):
        self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': qty})

    def _payload(self, **extra):
        data = {
            'customer_name': 'Олена Тест',
            'customer_email': 'guest@example.com',
            'customer_phone': '+380671112233',
            'shipping_method': 'pickup_salon',
            'payment_method': 'bank',
            'salon_id': str(self.salon.pk),
        }
        data.update(extra)
        return data

    def test_empty_checkout_redirects_to_cart(self):
        response = self.client.get(self.checkout_url)
        self.assertRedirects(response, reverse('commerce:cart'))

    def test_guest_order_user_is_null(self):
        self._fill_cart()
        response = self.client.post(self.checkout_url, self._payload())
        self.assertRedirects(response, self.thanks_url)
        order = Order.objects.get()
        self.assertIsNone(order.user)
        self.assertEqual(order.total_uah, Decimal('15000.00'))
        self.assertEqual(order.pickup_salon_name, 'Atelier Test')
        self.assertIn('Львів', order.pickup_salon_address)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty, 1)
        cart = Cart.objects.get()
        self.assertEqual(cart.status, Cart.Status.CONVERTED)

    def test_thanks_requires_session_pair(self):
        self.assertEqual(self.client.get(self.thanks_url).status_code, 404)
        self._fill_cart()
        self.client.post(self.checkout_url, self._payload())
        thanks = self.client.get(self.thanks_url)
        self.assertEqual(thanks.status_code, 200)
        self.assertContains(thanks, Order.objects.get().number)
        session = self.client.session
        session['last_order_number'] = 'FAKE'
        session.save()
        self.assertEqual(self.client.get(self.thanks_url).status_code, 404)

    def test_price_from_product_not_post(self):
        self._fill_cart()
        self.client.post(
            self.checkout_url,
            self._payload(unit_price='1', total='1', price_uah='1'),
        )
        order = Order.objects.get()
        self.assertEqual(order.total_uah, Decimal('15000.00'))
        item = OrderItem.objects.get()
        self.assertEqual(item.unit_price_uah, Decimal('15000.00'))

    def test_over_stock_rejected(self):
        self._fill_cart(qty=1)
        cart = Cart.objects.get()
        line = CartItem.objects.get(cart=cart)
        line.qty = 5
        line.save()
        response = self.client.post(self.checkout_url, self._payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Order.objects.count(), 0)
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock_qty, 2)

    def test_np_warehouse_order(self):
        self._fill_cart()
        response = self.client.post(
            self.checkout_url,
            self._payload(
                shipping_method='np_warehouse',
                salon_id='',
                np_city_ref='lviv',
                np_city_name='Львів',
                np_warehouse_ref='lviv-1',
                np_warehouse_name='Відділення №1, вул. Городоцька, 157',
            ),
        )
        self.assertRedirects(response, self.thanks_url)
        order = Order.objects.get()
        self.assertEqual(order.np_city_name, 'Львів')
        self.assertEqual(order.np_warehouse_ref, 'lviv-1')

    def test_auth_order_keeps_user(self):
        user = User.objects.create_user(
            email='buyer@example.com',
            password='StrongPass123!',
            first_name='Марія',
        )
        self.client.force_login(user)
        self._fill_cart()
        self.client.post(self.checkout_url, self._payload(customer_email=user.email))
        order = Order.objects.get()
        self.assertEqual(order.user, user)

    def test_np_cities_stub(self):
        response = self.client.get(reverse('commerce:np_cities'), {'q': 'льв'})
        self.assertEqual(response.status_code, 200)
        names = [row['name'] for row in response.json()['results']]
        self.assertIn('Львів', names)
