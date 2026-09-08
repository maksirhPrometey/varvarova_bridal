from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from src.catalog.models import Category, Product
from src.commerce.models import Cart, CartItem
from src.commerce.services import merge_guest_cart
from src.users.models import User


class CartFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Весільні', slug='wedding')
        self.product = Product.objects.create(
            category=self.category,
            sku='T-CART-1',
            slug='amber-cart',
            name='Amber',
            price_uah=Decimal('10000.00'),
            stock_qty=3,
        )
        self.oos = Product.objects.create(
            category=self.category,
            sku='T-CART-0',
            slug='thea-cart',
            name='Thea',
            price_uah=Decimal('5000.00'),
            stock_qty=0,
        )
        self.add_url = reverse('commerce:cart_add')
        self.cart_url = reverse('commerce:cart')

    def test_guest_add_and_page(self):
        response = self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 1})
        self.assertRedirects(response, self.cart_url)
        page = self.client.get(self.cart_url)
        self.assertContains(page, 'Amber')
        self.assertContains(page, '10000 грн')
        self.assertContains(page, 'id="cart-count"')
        self.assertContains(page, '>1<')
        self.assertEqual(CartItem.objects.count(), 1)

    def test_add_increments_same_line(self):
        self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 1})
        self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 1})
        self.assertEqual(CartItem.objects.count(), 1)
        self.assertEqual(CartItem.objects.get().qty, 2)

    def test_add_over_stock_is_400(self):
        response = self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 4})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Недостатньо', response.content.decode())
        self.assertEqual(CartItem.objects.count(), 0)

    def test_zero_stock_is_400(self):
        response = self.client.post(self.add_url, {'product_id': self.oos.pk, 'qty': 1})
        self.assertEqual(response.status_code, 400)
        self.assertIn('наявності', response.content.decode())

    def test_inactive_product_is_400(self):
        self.product.is_active = False
        self.product.save(update_fields=['is_active'])
        response = self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 1})
        self.assertEqual(response.status_code, 400)

    def test_qty_and_remove(self):
        self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 2})
        item = CartItem.objects.get()
        qty_url = reverse('commerce:cart_qty')
        self.client.post(qty_url, {'item_id': item.pk, 'qty': 1})
        item.refresh_from_db()
        self.assertEqual(item.qty, 1)
        over = self.client.post(qty_url, {'item_id': item.pk, 'qty': 9})
        self.assertEqual(over.status_code, 400)
        self.client.post(reverse('commerce:cart_remove'), {'item_id': item.pk})
        self.assertEqual(CartItem.objects.count(), 0)

    def test_cannot_change_foreign_item(self):
        user = User.objects.create_user(email='owner@example.com', password='StrongPass123!')
        cart = Cart.objects.create(user=user, status=Cart.Status.ACTIVE)
        item = CartItem.objects.create(cart=cart, product=self.product, qty=1)
        response = self.client.post(
            reverse('commerce:cart_qty'),
            {'item_id': item.pk, 'qty': 2},
        )
        self.assertEqual(response.status_code, 400)
        item.refresh_from_db()
        self.assertEqual(item.qty, 1)

    def test_htmx_add_swaps_button_and_count(self):
        response = self.client.post(
            self.add_url,
            {'product_id': self.product.pk, 'qty': 1},
            HTTP_HX_REQUEST='true',
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Додано')
        self.assertContains(response, 'hx-swap-oob')
        self.assertContains(response, '>1<')

    def test_merge_caps_qty_by_stock(self):
        user = User.objects.create_user(email='bride@example.com', password='StrongPass123!')
        user_cart = Cart.objects.create(user=user, status=Cart.Status.ACTIVE)
        CartItem.objects.create(cart=user_cart, product=self.product, qty=2)
        self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 2})
        guest_key = self.client.session.session_key
        merge_guest_cart(user, guest_key)
        user_cart.refresh_from_db()
        item = user_cart.items.get(product=self.product)
        self.assertEqual(item.qty, 3)
        guest = Cart.objects.get(session_key=guest_key)
        self.assertEqual(guest.status, Cart.Status.CONVERTED)

    def test_login_merges_guest_cart(self):
        user = User.objects.create_user(
            email='merge@example.com',
            password='StrongPass123!',
            first_name='Олена',
        )
        self.client.post(self.add_url, {'product_id': self.product.pk, 'qty': 1})
        self.client.post(
            reverse('authentication:login'),
            {'username': 'merge@example.com', 'password': 'StrongPass123!'},
        )
        cart = Cart.objects.get(user=user, status=Cart.Status.ACTIVE)
        self.assertEqual(cart.items.get().qty, 1)
        self.assertIsNone(cart.session_key)
