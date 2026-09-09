from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from src.content.home_models import HomePage  # noqa: F401
from src.content.landing_models import (  # noqa: F401
    CarePage,
    ContactsPage,
    DeliveryPage,
    OfferPage,
    PartnershipPage,
    PrivacyPage,
)
from src.core.models import CreatedAtModel, SeoFieldsMixin, TimeStampedModel, UpdatedAtModel


class SiteSettings(UpdatedAtModel):
    site_name = models.CharField('Назва сайту', max_length=255)
    logo = models.ImageField(
        'Логотип',
        upload_to='settings/',
        max_length=255,
        null=True,
        blank=True,
    )
    contacts_json = models.JSONField('Контакти', default=dict)
    robots_txt = models.TextField('robots.txt', null=True, blank=True)

    class Meta:
        db_table = 'content_site_settings'
        verbose_name = 'Налаштування сайту'
        verbose_name_plural = 'Налаштування сайту'
        constraints = [
            models.CheckConstraint(
                condition=Q(id=1),
                name='content_site_settings_singleton',
            ),
        ]

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Singleton не можна видаляти.')

    @classmethod
    def load(cls) -> 'SiteSettings':
        obj, _created = cls.objects.get_or_create(
            pk=1,
            defaults={'site_name': 'Varvarova', 'contacts_json': {}},
        )
        return obj

    def __str__(self) -> str:
        return self.site_name


TYPED_PAGE_SLUGS = frozenset({
    'about',
    'partnership',
    'delivery',
    'care',
    'offer',
    'privacy',
    'contacts',
})


class Page(SeoFieldsMixin, UpdatedAtModel):
    slug = models.SlugField('Slug', max_length=128, unique=True)
    title = models.CharField('Заголовок', max_length=255)
    body = models.TextField('Текст')
    is_published = models.BooleanField('Опубліковано', default=False)

    class Meta:
        db_table = 'content_page'
        verbose_name = 'Сторінка'
        verbose_name_plural = 'Сторінки'

    def clean(self):
        super().clean()
        if self.slug in TYPED_PAGE_SLUGS:
            raise ValidationError(
                {'slug': 'Цю сторінку редагують окремим пунктом у Контент.'}
            )

    def __str__(self) -> str:
        return self.title


class AboutPage(SeoFieldsMixin, UpdatedAtModel):
    page_title = models.CharField(
        'Назва у вкладці',
        max_length=128,
        help_text='Заголовок вкладки браузера. Якщо SEO-заголовок порожній — візьметься він.',
    )
    eyebrow = models.CharField(
        'Надзаголовок',
        max_length=64,
        help_text='Дрібний рядок над великим заголовком, зараз «Філософія».',
    )
    heading = models.CharField(
        'Заголовок',
        max_length=128,
        help_text='Текст до курсиву, зараз «Світ».',
    )
    heading_em = models.CharField(
        'Виділене слово',
        max_length=64,
        blank=True,
        help_text='Курсив у заголовку, зараз «VARVAROVA». Можна лишити порожнім.',
    )
    lede = models.TextField(
        'Лід',
        help_text='Перший абзац під заголовком.',
    )
    body = models.TextField(
        'Основний текст',
        help_text='Другий абзац під лідом.',
    )
    is_published = models.BooleanField('Опубліковано', default=True)

    class Meta:
        db_table = 'content_about_page'
        verbose_name = 'Про бренд'
        verbose_name_plural = 'Про бренд'
        constraints = [
            models.CheckConstraint(
                condition=Q(id=1),
                name='content_about_page_singleton',
            ),
        ]

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Singleton не можна видаляти.')

    @classmethod
    def load(cls) -> 'AboutPage':
        from src.content.stubs import ABOUT_DEFAULTS

        obj, _created = cls.objects.get_or_create(pk=1, defaults=ABOUT_DEFAULTS)
        return obj

    def __str__(self) -> str:
        return self.page_title or 'Про бренд'


class FaqItem(models.Model):
    question = models.CharField('Питання', max_length=512)
    answer = models.TextField('Відповідь')
    sort_order = models.IntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубліковано', default=False)

    class Meta:
        db_table = 'content_faq_item'
        verbose_name = 'FAQ'
        verbose_name_plural = 'FAQ'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.question


class BlogPost(SeoFieldsMixin, TimeStampedModel):
    slug = models.SlugField('Slug', max_length=255, unique=True)
    title = models.CharField('Заголовок', max_length=255)
    excerpt = models.CharField('Короткий опис', max_length=512, null=True, blank=True)
    body = models.TextField('Текст')
    cover_image = models.ImageField(
        'Обкладинка',
        upload_to='blog/%Y/%m/',
        max_length=255,
        null=True,
        blank=True,
    )
    published_at = models.DateTimeField('Дата публікації', null=True, blank=True)
    is_published = models.BooleanField('Опубліковано', default=False)

    class Meta:
        db_table = 'content_blog_post'
        verbose_name = 'Запис блогу'
        verbose_name_plural = 'Блог'

    def __str__(self) -> str:
        return self.title


class Review(CreatedAtModel):
    author_name = models.CharField('Автор', max_length=255)
    text = models.TextField('Текст')
    rating = models.SmallIntegerField('Оцінка', null=True, blank=True)
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews',
        verbose_name='Товар',
    )
    is_published = models.BooleanField('Опубліковано', default=False)
    sort_order = models.IntegerField('Порядок', default=0)

    class Meta:
        db_table = 'content_review'
        verbose_name = 'Відгук'
        verbose_name_plural = 'Відгуки'
        ordering = ['sort_order', 'id']
        constraints = [
            models.CheckConstraint(
                condition=Q(rating__isnull=True) | (Q(rating__gte=1) & Q(rating__lte=5)),
                name='content_review_rating_1_5',
            ),
        ]

    def __str__(self) -> str:
        return self.author_name


class Salon(models.Model):
    name = models.CharField('Назва', max_length=255)
    country = models.CharField('Країна', max_length=128, null=True, blank=True)
    city = models.CharField('Місто', max_length=128)
    address = models.CharField('Адреса', max_length=512)
    phone = models.CharField('Телефон', max_length=64, null=True, blank=True)
    email = models.EmailField('Email', null=True, blank=True)
    lat = models.DecimalField(
        'Широта',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    lng = models.DecimalField(
        'Довгота',
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    working_hours = models.CharField('Години роботи', max_length=255, null=True, blank=True)
    sort_order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        db_table = 'content_salon'
        verbose_name = 'Салон'
        verbose_name_plural = 'Салони'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.name


class Banner(models.Model):
    title = models.CharField('Заголовок', max_length=255, null=True, blank=True)
    image = models.ImageField('Зображення', upload_to='banners/%Y/%m/', max_length=255)
    link_url = models.CharField('Посилання', max_length=512, null=True, blank=True)
    sort_order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активний', default=True)

    class Meta:
        db_table = 'content_banner'
        verbose_name = 'Банер'
        verbose_name_plural = 'Банери'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.title or f'Banner {self.pk}'


class TrunkShow(models.Model):
    home_page = models.ForeignKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name='events',
        verbose_name='Головна',
        default=1,
    )
    title = models.CharField('Назва', max_length=255, blank=True)
    city = models.CharField('Місто', max_length=128, null=True, blank=True)
    place = models.CharField('Місце', max_length=255, null=True, blank=True)
    starts_at = models.DateTimeField('Початок')
    ends_at = models.DateTimeField('Кінець', null=True, blank=True)
    description = models.TextField('Опис', null=True, blank=True)
    is_published = models.BooleanField('Опубліковано', default=False)

    class Meta:
        db_table = 'content_trunk_show'
        verbose_name = 'Подія'
        verbose_name_plural = 'Події'
        ordering = ['-starts_at']

    def clean(self):
        super().clean()
        if not (self.city or self.title):
            raise ValidationError({'city': 'Вкажіть місто.'})

    def save(self, *args, **kwargs):
        if not self.home_page_id:
            self.home_page_id = 1
        if not self.title:
            self.title = (self.city or self.place or 'Подія')[:255]
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.city or self.title or 'Подія'


class BrideGalleryItem(models.Model):
    title = models.CharField('Заголовок', max_length=255, null=True, blank=True)
    image = models.ImageField('Зображення', upload_to='brides/%Y/%m/', max_length=255)
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bride_gallery_items',
        verbose_name='Товар',
    )
    sort_order = models.IntegerField('Порядок', default=0)
    is_published = models.BooleanField('Опубліковано', default=False)

    class Meta:
        db_table = 'content_bride_gallery_item'
        verbose_name = 'Наречена'
        verbose_name_plural = 'Наречені'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.title or f'Bride {self.pk}'


class PartnerApplication(CreatedAtModel):
    class Status(models.TextChoices):
        NEW = 'new', 'Нова'
        IN_PROGRESS = 'in_progress', 'В роботі'
        DONE = 'done', 'Оброблена'
        REJECTED = 'rejected', 'Відхилена'

    company_name = models.CharField('Компанія', max_length=255)
    contact_name = models.CharField('Контакт', max_length=255)
    email = models.EmailField('Email')
    phone = models.CharField('Телефон', max_length=32)
    city = models.CharField('Місто', max_length=128, null=True, blank=True)
    message = models.TextField('Повідомлення', null=True, blank=True)
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )

    class Meta:
        db_table = 'content_partner_application'
        verbose_name = 'Заявка партнера'
        verbose_name_plural = 'Заявки партнерів'
        ordering = ['-created_at']

    def __str__(self) -> str:
        return self.company_name


class FittingRequest(CreatedAtModel):
    class Status(models.TextChoices):
        NEW = 'new', 'Нова'
        IN_PROGRESS = 'in_progress', 'В роботі'
        DONE = 'done', 'Оброблена'

    name = models.CharField('Імʼя', max_length=255)
    phone = models.CharField('Телефон', max_length=32)
    email = models.EmailField('Email', null=True, blank=True)
    product = models.ForeignKey(
        'catalog.Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='fitting_requests',
        verbose_name='Модель',
    )
    product_name = models.CharField('Модель', max_length=255, blank=True)
    message = models.TextField('Коментар', null=True, blank=True)
    status = models.CharField(
        'Статус',
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )

    class Meta:
        db_table = 'content_fitting_request'
        verbose_name = 'Заявка на примірку'
        verbose_name_plural = 'Заявки на примірку'
        ordering = ['-created_at']

    def __str__(self) -> str:
        if self.product_name:
            return f'{self.name} — {self.product_name}'
        return self.name
