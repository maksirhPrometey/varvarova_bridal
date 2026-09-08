from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from src.catalog.models import Category, Product
from src.commerce.models import Order, OrderItem
from src.users.models import User


class AccountOrderTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='StrongPass123!',
            first_name='Олена',
        )
        self.other = User.objects.create_user(
            email='other@example.com',
            password='StrongPass123!',
            first_name='Інша',
        )
        self.staff = User.objects.create_user(
            email='staff@example.com',
            password='StrongPass123!',
            is_staff=True,
            role=User.Role.MANAGER,
        )
        category = Category.objects.create(name='Test', slug='test-cat')
        product = Product.objects.create(
            category=category,
            sku='T-1',
            slug='test-dress',
            name='Test',
            price_uah=Decimal('1000.00'),
            stock_qty=2,
        )
        self.order = Order.objects.create(
            number='VV-TEST-1',
            user=self.owner,
            customer_name='Олена',
            customer_email=self.owner.email,
            customer_phone='+380670000000',
            subtotal_uah=product.price_uah,
            total_uah=product.price_uah,
            payment_method='bank',
            shipping_method=Order.ShippingMethod.PICKUP_SALON,
        )
        OrderItem.objects.create(
            order=self.order,
            product=product,
            sku_snapshot=product.sku,
            name_snapshot=product.name,
            unit_price_uah=product.price_uah,
            qty=1,
            line_total_uah=product.price_uah,
        )

    def test_owner_sees_order(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse('commerce:account_orders'))
        self.assertContains(response, 'VV-TEST-1')
        detail = self.client.get(
            reverse('commerce:account_order_detail', kwargs={'number': 'VV-TEST-1'})
        )
        self.assertEqual(detail.status_code, 200)
        self.assertContains(detail, 'Test')

    def test_foreign_number_is_404(self):
        self.client.force_login(self.other)
        response = self.client.get(
            reverse('commerce:account_order_detail', kwargs={'number': 'VV-TEST-1'})
        )
        self.assertEqual(response.status_code, 404)

    def test_staff_can_open_by_number(self):
        self.client.force_login(self.staff)
        response = self.client.get(
            reverse('commerce:account_order_detail', kwargs={'number': 'VV-TEST-1'})
        )
        self.assertEqual(response.status_code, 200)
