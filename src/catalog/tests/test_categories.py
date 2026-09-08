from django.test import TestCase
from django.urls import reverse

from src.catalog.models import Category


class CatalogCategoryTreeTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.wedding = Category.objects.create(
            name='Весільні сукні',
            slug='wedding',
            sort_order=10,
            is_active=True,
        )
        cls.accessories = Category.objects.create(
            name='Аксесуари',
            slug='accessories',
            sort_order=30,
            is_active=True,
            description='Фати та рукавички.',
        )
        Category.objects.create(
            name='Фати',
            slug='accessories-veils',
            parent=cls.accessories,
            sort_order=31,
            is_active=True,
        )
        Category.objects.create(
            name='Рукавички',
            slug='accessories-gloves',
            parent=cls.accessories,
            sort_order=32,
            is_active=True,
        )
        cls.lingerie = Category.objects.create(
            name='Весільна білизна',
            slug='lingerie',
            sort_order=40,
            is_active=True,
        )
        Category.objects.create(
            name='Бюстгальтери',
            slug='lingerie-bras',
            parent=cls.lingerie,
            sort_order=41,
            is_active=True,
        )

    def test_accessories_root(self):
        response = self.client.get(reverse('catalog:list', kwargs={'slug': 'accessories'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Аксесуари')
        self.assertContains(response, 'Фати')
        self.assertContains(response, 'Рукавички')

    def test_lingerie_root(self):
        response = self.client.get(reverse('catalog:list', kwargs={'slug': 'lingerie'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Весільна білизна')
        self.assertContains(response, 'Бюстгальтери')

    def test_accessories_child_empty_grid(self):
        response = self.client.get(
            reverse('catalog:list', kwargs={'slug': 'accessories-gloves'})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Рукавички')
        self.assertContains(response, 'Аксесуари')
        self.assertContains(response, 'Поки немає моделей у цій категорії.')

    def test_wedding_still_ok(self):
        response = self.client.get(reverse('catalog:list', kwargs={'slug': 'wedding'}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Весільні сукні')
