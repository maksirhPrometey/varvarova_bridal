from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from src.core.models import SeoFieldsMixin, UpdatedAtModel


class HomePage(SeoFieldsMixin, UpdatedAtModel):
    page_title = models.CharField(
        'Назва у вкладці',
        max_length=128,
        help_text='Заголовок вкладки браузера, якщо SEO-заголовок порожній.',
    )
    hero_image = models.ImageField(
        'Фото банера',
        upload_to='home/',
        max_length=255,
        null=True,
        blank=True,
        help_text='Повноекранне фото героя. Якщо порожньо — світлий фон без знімка.',
    )
    hero_eyebrow = models.CharField(
        'Надзаголовок банера',
        max_length=64,
        help_text='Дрібний рядок над H1, зараз «Колекція 2026».',
    )
    hero_heading = models.CharField(
        'Заголовок банера',
        max_length=128,
        help_text='Великий H1, зараз «Varvarova».',
    )
    hero_text = models.TextField(
        'Текст банера',
        help_text='Абзац під заголовком.',
    )
    hero_cta = models.CharField(
        'Кнопка банера',
        max_length=64,
        help_text='Зараз «Переглянути». Веде в каталог весільних.',
    )
    bestsellers_eyebrow = models.CharField('Бестселери — надзаголовок', max_length=64)
    bestsellers_title = models.CharField('Бестселери — заголовок', max_length=128)
    bestsellers_link = models.CharField('Бестселери — посилання', max_length=64)
    b2b_eyebrow = models.CharField('B2B — надзаголовок', max_length=64)
    b2b_title = models.CharField('B2B — заголовок', max_length=128)
    b2b_text = models.TextField('B2B — текст')
    b2b_cta = models.CharField('B2B — кнопка', max_length=64)
    couture_eyebrow = models.CharField('Couture — надзаголовок', max_length=64)
    couture_title = models.CharField('Couture — заголовок', max_length=128)
    couture_text = models.TextField('Couture — текст')
    couture_cta = models.CharField('Couture — кнопка', max_length=64)
    events_is_visible = models.BooleanField(
        'Показувати блок подій',
        default=True,
        help_text='Вимкніть, щоб сховати всю секцію. Картки нижче не видаляються.',
    )
    events_eyebrow = models.CharField('Події — надзаголовок', max_length=64)
    events_title = models.CharField('Події — заголовок', max_length=128)
    events_intro = models.TextField('Події — лід', blank=True)
    events_cta = models.CharField('Події — посилання', max_length=64)
    is_published = models.BooleanField('Опубліковано', default=True)

    class Meta:
        db_table = 'content_home_page'
        verbose_name = 'Головна'
        verbose_name_plural = 'Головна'
        constraints = [
            models.CheckConstraint(
                condition=Q(id=1),
                name='content_home_page_singleton',
            ),
        ]

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValidationError('Singleton не можна видаляти.')

    @classmethod
    def load(cls) -> 'HomePage':
        from src.content.stubs import HOME_DEFAULTS

        obj, _created = cls.objects.get_or_create(pk=1, defaults=HOME_DEFAULTS)
        return obj

    def __str__(self) -> str:
        return self.page_title or 'Головна'
