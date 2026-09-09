from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin, TabularInline

from src.content.admin_forms import (
    AboutPageAdminForm,
    CarePageAdminForm,
    ContactsPageAdminForm,
    DeliveryPageAdminForm,
    HomePageAdminForm,
    OfferPageAdminForm,
    PartnershipPageAdminForm,
    PrivacyPageAdminForm,
)
from src.content.landing_models import PartnershipPage
from src.content.models import AboutPage, TrunkShow
from src.core.admin import SEO_FIELDSET


class SingletonAdmin(ModelAdmin):
    def has_add_permission(self, request) -> bool:
        return not self.model.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        obj = self.model.load()
        return HttpResponseRedirect(
            reverse(f'admin:{self.model._meta.app_label}_{self.model._meta.model_name}_change', args=[obj.pk])
        )


class AboutPageAdmin(SingletonAdmin):
    form = AboutPageAdminForm
    readonly_fields = ('heading_preview', 'updated_at')
    fieldsets = (
        (
            'Герой',
            {
                'description': (
                    'Ці поля мапляться 1:1 на блок на /about/. '
                    'Надзаголовок → дрібний рядок, заголовок + виділене слово → великий H1.'
                ),
                'fields': (
                    'eyebrow',
                    'heading',
                    'heading_em',
                    'heading_preview',
                ),
            },
        ),
        (
            'Текст',
            {
                'description': 'Лід — перший абзац, основний текст — другий.',
                'fields': ('lede', 'body'),
            },
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
    )

    def heading_preview(self, obj):
        if not obj or not obj.heading:
            return '—'
        if obj.heading_em:
            return format_html('{} <em>{}</em>', obj.heading, obj.heading_em)
        return obj.heading

    heading_preview.short_description = 'Як виглядає H1'


class PartnershipPageAdmin(SingletonAdmin):
    form = PartnershipPageAdminForm
    readonly_fields = ('updated_at',)
    fieldsets = (
        (
            'Герой',
            {
                'description': 'Верхній блок на /partnership/. Фото — права колонка.',
                'fields': ('eyebrow', 'heading', 'body', 'hero_image'),
            },
        ),
        (
            'Бенефіти',
            {
                'description': 'Три картки під героєм. Порожня назва і текст — картка не покажеться.',
                'fields': (
                    'benefits_eyebrow',
                    'benefits_title',
                    'benefit_1_title',
                    'benefit_1_text',
                    'benefit_2_title',
                    'benefit_2_text',
                    'benefit_3_title',
                    'benefit_3_text',
                ),
            },
        ),
        (
            'Форма заявки',
            {
                'description': (
                    'Підписи полів і кнопка на вітрині. '
                    'Заявки падають у Продажі → Заявки партнерів.'
                ),
                'fields': (
                    'form_eyebrow',
                    'form_title',
                    'label_company',
                    'label_contact',
                    'label_email',
                    'label_phone',
                    'label_city',
                    'label_message',
                    'form_submit',
                    'form_note',
                    'form_success',
                ),
            },
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
    )


class DeliveryPageAdmin(SingletonAdmin):
    form = DeliveryPageAdminForm
    readonly_fields = ('updated_at',)
    fieldsets = (
        (
            'Герой',
            {
                'description': 'Верхній блок на /delivery/.',
                'fields': ('eyebrow', 'heading', 'lede'),
            },
        ),
        (
            'Доставка',
            {
                'description': 'Перший блок. Порожні заголовок і текст — секція не покажеться.',
                'fields': ('delivery_title', 'delivery_text'),
            },
        ),
        (
            'Оплата',
            {'fields': ('payment_title', 'payment_text')},
        ),
        (
            'Повернення',
            {'fields': ('returns_title', 'returns_text')},
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
    )


class CarePageAdmin(SingletonAdmin):
    form = CarePageAdminForm
    readonly_fields = ('updated_at',)
    fieldsets = (
        (
            'Герой',
            {
                'description': 'Верхній блок на /care/.',
                'fields': ('eyebrow', 'heading', 'lede'),
            },
        ),
        (
            'Зберігання',
            {
                'description': 'Перший блок. Порожні заголовок і текст — секція не покажеться.',
                'fields': ('storage_title', 'storage_text'),
            },
        ),
        (
            'Чистка',
            {'fields': ('cleaning_title', 'cleaning_text')},
        ),
        (
            'Після церемонії',
            {'fields': ('aftercare_title', 'aftercare_text')},
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
    )


class OfferPageAdmin(SingletonAdmin):
    form = OfferPageAdminForm
    readonly_fields = ('updated_at',)
    fieldsets = (
        (
            'Герой',
            {
                'description': 'Верхній блок на /offer/.',
                'fields': ('eyebrow', 'heading', 'lede'),
            },
        ),
        (
            'Предмет',
            {
                'description': 'Перший блок. Порожні заголовок і текст — секція не покажеться.',
                'fields': ('subject_title', 'subject_text'),
            },
        ),
        (
            'Акцепт',
            {'fields': ('acceptance_title', 'acceptance_text')},
        ),
        (
            'Умови',
            {'fields': ('conditions_title', 'conditions_text')},
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
    )


class PrivacyPageAdmin(SingletonAdmin):
    form = PrivacyPageAdminForm
    readonly_fields = ('updated_at',)
    fieldsets = (
        (
            'Герой',
            {
                'description': 'Верхній блок на /privacy/.',
                'fields': ('eyebrow', 'heading', 'lede'),
            },
        ),
        (
            'Які дані',
            {
                'description': 'Перший блок. Порожні заголовок і текст — секція не покажеться.',
                'fields': ('data_title', 'data_text'),
            },
        ),
        (
            'Навіщо',
            {'fields': ('purpose_title', 'purpose_text')},
        ),
        (
            'Передача',
            {'fields': ('sharing_title', 'sharing_text')},
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
    )


class ContactsPageAdmin(SingletonAdmin):
    form = ContactsPageAdminForm
    readonly_fields = ('updated_at',)
    fieldsets = (
        (
            'Герой',
            {
                'description': 'Верхній блок на /contacts/. Телефон і email — у Налаштуваннях сайту.',
                'fields': ('eyebrow', 'heading', 'lede'),
            },
        ),
        (
            'Підписи',
            {
                'description': 'Підписи перед значеннями з Налаштувань сайту. Порожній підпис — лише значення.',
                'fields': (
                    'phone_label',
                    'email_label',
                    'address_label',
                    'instagram_label',
                ),
            },
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
    )


class TrunkShowInline(TabularInline):
    model = TrunkShow
    extra = 1
    fields = ('city', 'place', 'starts_at', 'ends_at', 'is_published')


class HomePageAdmin(SingletonAdmin):
    form = HomePageAdminForm
    readonly_fields = ('updated_at',)
    inlines = (TrunkShowInline,)
    fieldsets = (
        (
            'Банер',
            {
                'description': 'Повноекранний герой на головній. Фото — тут, не в окремому пункті.',
                'fields': (
                    'hero_image',
                    'hero_eyebrow',
                    'hero_heading',
                    'hero_text',
                    'hero_cta',
                ),
            },
        ),
        (
            'Бестселери',
            {
                'fields': (
                    'bestsellers_eyebrow',
                    'bestsellers_title',
                    'bestsellers_link',
                ),
            },
        ),
        (
            'B2B',
            {
                'description': 'Порожні заголовок і текст — секція не покажеться.',
                'fields': ('b2b_eyebrow', 'b2b_title', 'b2b_text', 'b2b_cta'),
            },
        ),
        (
            'Couture',
            {
                'fields': (
                    'couture_eyebrow',
                    'couture_title',
                    'couture_text',
                    'couture_cta',
                ),
            },
        ),
        (
            'Вкладка браузера',
            {'fields': ('page_title', 'is_published')},
        ),
        SEO_FIELDSET,
        ('Службове', {'fields': ('updated_at',)}),
        (
            'Події',
            {
                'description': (
                    'Галочка ховає всю секцію. Картки — у таблиці нижче: місто, місце, дати. '
                    'Зніміть «Опубліковано», щоб прибрати картку з сайту.'
                ),
                'fields': (
                    'events_is_visible',
                    'events_eyebrow',
                    'events_title',
                    'events_intro',
                    'events_cta',
                ),
            },
        ),
    )
