import json
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from src.catalog.models import Category, Product, WishlistItem
from src.catalog.services import merge_ids_for_user
from src.users.models import User


class WishlistTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Весільні', slug='wedding-wish')
        self.one = Product.objects.create(
            category=self.category,
            sku='W-1',
            slug='wish-one',
            name='One',
            price_uah=Decimal('1000.00'),
            stock_qty=2,
        )
        self.two = Product.objects.create(
            category=self.category,
            sku='W-2',
            slug='wish-two',
            name='Two',
            price_uah=Decimal('2000.00'),
            stock_qty=2,
        )
        self.three = Product.objects.create(
            category=self.category,
            sku='W-3',
            slug='wish-three',
            name='Three',
            price_uah=Decimal('3000.00'),
            stock_qty=1,
        )
        self.inactive = Product.objects.create(
            category=self.category,
            sku='W-X',
            slug='wish-off',
            name='Off',
            price_uah=Decimal('500.00'),
            stock_qty=1,
            is_active=False,
        )
        self.toggle_url = reverse('catalog:wishlist_toggle')
        self.merge_url = reverse('catalog:wishlist_merge')
        self.page_url = reverse('catalog:wishlist')

    def _post_json(self, url, payload, **extra):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type='application/json',
            **extra,
        )

    def test_guest_page_with_ids(self):
        response = self.client.get(self.page_url, {'ids': f'{self.one.pk},{self.inactive.pk},999'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'One')
        self.assertNotContains(response, 'Off')

    def test_toggle_requires_auth(self):
        response = self._post_json(self.toggle_url, {'product_id': self.one.pk})
        self.assertEqual(response.status_code, 401)

    def test_toggle_add_and_remove(self):
        user = User.objects.create_user(email='wish@example.com', password='StrongPass123!')
        self.client.force_login(user)
        added = self._post_json(self.toggle_url, {'product_id': self.one.pk})
        self.assertEqual(added.status_code, 200)
        body = added.json()
        self.assertTrue(body['in_wishlist'])
        self.assertEqual(body['count'], 1)
        removed = self._post_json(self.toggle_url, {'product_id': self.one.pk})
        self.assertFalse(removed.json()['in_wishlist'])
        self.assertEqual(removed.json()['count'], 0)

    def test_toggle_inactive_is_400(self):
        user = User.objects.create_user(email='wish2@example.com', password='StrongPass123!')
        self.client.force_login(user)
        response = self._post_json(self.toggle_url, {'product_id': self.inactive.pk})
        self.assertEqual(response.status_code, 400)

    def test_merge_unions_and_skips_unknown(self):
        user = User.objects.create_user(email='mergew@example.com', password='StrongPass123!')
        WishlistItem.objects.create(user=user, product=self.one)
        WishlistItem.objects.create(user=user, product=self.two)
        count = merge_ids_for_user(
            user,
            [self.two.pk, self.three.pk, self.inactive.pk, 99999, self.one.pk],
        )
        self.assertEqual(count, 3)
        ids = set(
            WishlistItem.objects.filter(user=user).values_list('product_id', flat=True)
        )
        self.assertEqual(ids, {self.one.pk, self.two.pk, self.three.pk})

    def test_merge_endpoint(self):
        user = User.objects.create_user(email='mergeapi@example.com', password='StrongPass123!')
        self.client.force_login(user)
        response = self._post_json(self.merge_url, {'ids': [self.one.pk, self.two.pk]})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 2)

    def test_auth_page_lists_own_items(self):
        user = User.objects.create_user(email='page@example.com', password='StrongPass123!')
        WishlistItem.objects.create(user=user, product=self.two)
        self.client.force_login(user)
        response = self.client.get(self.page_url)
        self.assertContains(response, 'Two')
        self.assertNotContains(response, 'One')
