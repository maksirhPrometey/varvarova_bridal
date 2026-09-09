from datetime import timedelta
from io import BytesIO

from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import NoReverseMatch, reverse
from django.utils import timezone
from PIL import Image

from src.content.home_models import HomePage
from src.content.models import TrunkShow
from src.content.stubs import HOME_DEFAULTS
from src.users.models import User
from src.users.roles import GROUP_EDITOR, sync_staff_groups


def _png(name: str) -> SimpleUploadedFile:
    buffer = BytesIO()
    Image.new('RGB', (8, 8), 'white').save(buffer, 'PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


class HomePageTests(TestCase):
    def setUp(self):
        self.page = HomePage.load()
        self.url = reverse('content:home')

    def test_storefront_uses_model_fields(self):
        self.page.hero_eyebrow = 'Сезон весіль'
        self.page.hero_heading = 'Нова колекція'
        self.page.hero_cta = 'Дивитись сукні'
        self.page.b2b_title = 'Салонам'
        self.page.is_published = True
        self.page.save()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Сезон весіль')
        self.assertContains(response, 'Нова колекція')
        self.assertContains(response, 'Дивитись сукні')
        self.assertContains(response, 'Салонам')
        self.assertContains(response, '<h1 class="vv-hero__title">Нова колекція</h1>', html=True)

    def test_unpublished_falls_back_but_keeps_image(self):
        self.page.hero_image = _png('home-hero.png')
        self.page.hero_heading = 'Чернетка'
        self.page.is_published = False
        self.page.save()
        response = self.client.get(self.url)
        self.assertContains(response, HOME_DEFAULTS['hero_heading'])
        self.assertNotContains(response, 'Чернетка')
        self.assertContains(response, 'тимчасова заглушка')
        self.assertContains(response, self.page.hero_image.url)

    def test_empty_b2b_hidden(self):
        self.page.b2b_title = ''
        self.page.b2b_text = ''
        self.page.is_published = True
        self.page.save()
        response = self.client.get(self.url)
        self.assertNotContains(response, 'id="b2b"')
        self.assertContains(response, self.page.bestsellers_title)

    def test_events_can_be_hidden(self):
        TrunkShow.objects.create(
            title='Trunk Show — Paris',
            city='Париж',
            starts_at=timezone.now() + timedelta(days=10),
            is_published=True,
        )
        self.page.events_is_visible = False
        self.page.is_published = True
        self.page.save()
        hidden = self.client.get(self.url)
        self.assertNotContains(hidden, 'id="events"')
        self.page.events_is_visible = True
        self.page.save()
        shown = self.client.get(self.url)
        self.assertContains(shown, 'id="events"')
        self.assertContains(shown, 'Париж')

    def test_admin_is_singleton_and_hides_banner(self):
        admin = User.objects.create_superuser(
            email='home-admin@example.com',
            password='StrongPass123!',
        )
        self.client.force_login(admin)
        listing = self.client.get(reverse('admin:content_homepage_changelist'))
        self.assertEqual(listing.status_code, 302)
        self.assertIn('/admin/content/homepage/1/change/', listing.url)
        form = self.client.get(reverse('admin:content_homepage_change', args=[1]))
        self.assertEqual(form.status_code, 200)
        self.assertContains(form, 'Фото банера')
        self.assertContains(form, 'B2B — заголовок')
        self.assertContains(form, 'Показувати блок подій')
        self.assertContains(form, 'Місто')
        self.assertContains(form, 'Початок')
        with self.assertRaises(NoReverseMatch):
            reverse('admin:content_banner_changelist')
        with self.assertRaises(NoReverseMatch):
            reverse('admin:content_trunkshow_changelist')

    def test_editor_can_open(self):
        sync_staff_groups()
        editor = User.objects.create_user(
            email='home-editor@example.com',
            password='StrongPass123!',
            is_staff=True,
        )
        editor.groups.add(Group.objects.get(name=GROUP_EDITOR))
        self.client.force_login(editor)
        response = self.client.get(reverse('admin:content_homepage_change', args=[1]))
        self.assertEqual(response.status_code, 200)
