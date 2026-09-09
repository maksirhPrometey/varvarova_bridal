from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import timezone

from src.content.models import AboutPage, Review, TrunkShow
from src.users.models import User


class CmsAdminFormsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(
            email='cms-forms@example.com',
            password='StrongPass123!',
        )
        self.page = AboutPage.load()

    def test_generic_page_admin_removed(self):
        with self.assertRaises(NoReverseMatch):
            reverse('admin:content_page_changelist')

    def test_about_change_has_seo_and_updated(self):
        self.client.force_login(self.admin)
        response = self.client.get(
            reverse('admin:content_aboutpage_change', args=[self.page.pk]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SEO-заголовок')
        self.assertContains(response, 'Оновлено')

    def test_review_list_shows_excerpt(self):
        Review.objects.create(
            author_name='Олена',
            text='Дуже довгий текст відгуку, щоб перевірити скорочення в списку адмінки.',
            rating=5,
            is_published=True,
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin:content_review_changelist'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Дуже довгий текст')

    def test_trunk_show_inline_on_home(self):
        from src.content.home_models import HomePage

        HomePage.load()
        TrunkShow.objects.create(
            title='Показ',
            city='Львів',
            starts_at=timezone.now(),
            is_published=True,
        )
        self.client.force_login(self.admin)
        response = self.client.get(reverse('admin:content_homepage_change', args=[1]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Львів')
        self.assertContains(response, 'Початок')
        self.assertContains(response, 'Кінець')
        with self.assertRaises(NoReverseMatch):
            reverse('admin:content_trunkshow_change', args=[1])
