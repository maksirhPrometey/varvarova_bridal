from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display

from src.content.models import (
    AboutPage,
    BlogPost,
    BrideGalleryItem,
    FaqItem,
    PartnerApplication,
    FittingRequest,
    Review,
    Salon,
    SiteSettings,
)
from src.content.admin_forms import SiteSettingsAdminForm
from src.content.admin_landing import (
    AboutPageAdmin,
    CarePageAdmin,
    ContactsPageAdmin,
    DeliveryPageAdmin,
    HomePageAdmin,
    OfferPageAdmin,
    PartnershipPageAdmin,
    PrivacyPageAdmin,
)
from src.content.home_models import HomePage
from src.content.landing_models import (
    CarePage,
    ContactsPage,
    DeliveryPage,
    OfferPage,
    PartnershipPage,
    PrivacyPage,
)
from src.core.admin import TinyMCEAdminMixin, admin_photo_html

admin.site.register(HomePage, HomePageAdmin)
admin.site.register(AboutPage, AboutPageAdmin)
admin.site.register(CarePage, CarePageAdmin)
admin.site.register(DeliveryPage, DeliveryPageAdmin)
admin.site.register(OfferPage, OfferPageAdmin)
admin.site.register(PartnershipPage, PartnershipPageAdmin)
admin.site.register(PrivacyPage, PrivacyPageAdmin)
admin.site.register(ContactsPage, ContactsPageAdmin)


def _bulk_set_status(model_admin, request, queryset, to: str) -> None:
    updated = queryset.exclude(status=to).update(status=to)
    if updated:
        model_admin.message_user(
            request,
            f'Оновлено статусів: {updated}',
            messages.SUCCESS,
        )


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    form = SiteSettingsAdminForm
    readonly_fields = ('logo_preview', 'updated_at')
    fieldsets = (
        (None, {'fields': ('site_name', 'logo', 'logo_preview')}),
        (
            'Контакти',
            {'fields': ('phone', 'email', 'instagram', 'address')},
        ),
        (
            'Реквізити (оплата на рахунок)',
            {'fields': ('bank_recipient', 'bank_iban', 'bank_edrpou', 'bank_name')},
        ),
        ('SEO / robots', {'fields': ('robots_txt',)}),
        ('Службове', {'fields': ('updated_at',)}),
    )

    def has_add_permission(self, request) -> bool:
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None) -> bool:
        return False

    def changelist_view(self, request, extra_context=None):
        obj, _created = SiteSettings.objects.get_or_create(
            pk=1,
            defaults={'site_name': 'Varvarova', 'contacts_json': {}},
        )
        return HttpResponseRedirect(
            reverse('admin:content_sitesettings_change', args=[obj.pk])
        )

    def logo_preview(self, obj):
        if obj and obj.logo:
            return format_html('<img src="{}" alt="" width="120" height="120">', obj.logo.url)
        return '—'

    logo_preview.short_description = 'Превʼю логотипу'


@admin.register(FaqItem)
class FaqItemAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('answer',)
    list_display = ('question', 'is_published', 'sort_order')
    list_filter = ('is_published',)
    search_fields = ('question',)
    list_editable = ('is_published', 'sort_order')


@admin.register(BlogPost)
class BlogPostAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('body',)
    list_display = ('cover_thumb', 'title', 'is_published', 'published_at')
    list_display_links = ('cover_thumb', 'title')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'published_at'
    readonly_fields = ('cover_preview', 'created_at', 'updated_at')
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'excerpt', 'body')}),
        ('Обкладинка', {'fields': ('cover_image', 'cover_preview')}),
        ('Публікація', {'fields': ('is_published', 'published_at')}),
        ('SEO', {'fields': ('seo_title', 'seo_description', 'seo_keywords')}),
        ('Службове', {'fields': ('created_at', 'updated_at')}),
    )

    @display(description='Фото')
    def cover_thumb(self, obj: BlogPost):
        url = obj.cover_image.url if obj.cover_image else None
        return admin_photo_html(url, width=56, height=56)

    def cover_preview(self, obj):
        if obj and obj.cover_image:
            return format_html(
                '<img src="{}" alt="" width="160" height="160">',
                obj.cover_image.url,
            )
        return '—'

    cover_preview.short_description = 'Превʼю'


@admin.register(Review)
class ReviewAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('text',)
    list_display = (
        'author_name',
        'text_excerpt',
        'rating',
        'product',
        'is_published',
        'sort_order',
    )
    list_filter = ('is_published', 'rating')
    search_fields = ('author_name', 'text')
    list_editable = ('is_published', 'sort_order')
    autocomplete_fields = ('product',)
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('author_name', 'rating', 'product', 'text')}),
        ('Публікація', {'fields': ('is_published', 'sort_order')}),
        ('Службове', {'fields': ('created_at',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

    @display(description='Текст')
    def text_excerpt(self, obj: Review):
        text = (obj.text or '').strip()
        if len(text) > 72:
            return f'{text[:69]}…'
        return text or '—'


@admin.register(Salon)
class SalonAdmin(ModelAdmin):
    list_display = ('name', 'city', 'phone', 'is_active', 'sort_order')
    list_filter = ('is_active', 'country', 'city')
    search_fields = ('name', 'city', 'address', 'phone')
    list_editable = ('is_active', 'sort_order')
    fieldsets = (
        (
            'Вітрина',
            {
                'description': (
                    'Активні салони з’являються на сторінці /salony/ у списку та на карті. '
                    'Додайте партнерські точки в інших містах тут — пункт меню сам стане «Салони».'
                ),
                'fields': ('is_active', 'sort_order', 'name', 'city', 'country'),
            },
        ),
        ('Контакти', {'fields': ('address', 'phone', 'email', 'working_hours')}),
        ('Карта', {'fields': ('lat', 'lng')}),
    )


@admin.register(BrideGalleryItem)
class BrideGalleryItemAdmin(ModelAdmin):
    list_display = ('thumb', 'title', 'product', 'is_published', 'sort_order')
    list_display_links = ('thumb', 'title')
    list_filter = ('is_published',)
    list_editable = ('is_published', 'sort_order')
    search_fields = ('title',)
    autocomplete_fields = ('product',)
    readonly_fields = ('image_preview',)
    fields = (
        'title',
        'image',
        'image_preview',
        'product',
        'sort_order',
        'is_published',
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

    @display(description='Фото')
    def thumb(self, obj: BrideGalleryItem):
        url = obj.image.url if obj.image else None
        return admin_photo_html(url, width=56, height=56)

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" alt="" width="160" height="160">', obj.image.url)
        return '—'

    image_preview.short_description = 'Превʼю'


@admin.register(PartnerApplication)
class PartnerApplicationAdmin(ModelAdmin):
    list_display = (
        'company_name',
        'contact_name',
        'phone',
        'email',
        'city',
        'status_badge',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('company_name', 'contact_name', 'email', 'phone', 'city')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    actions = (
        'action_new',
        'action_in_progress',
        'action_done',
        'action_rejected',
    )
    fieldsets = (
        (
            'Компанія',
            {'fields': ('company_name', 'city')},
        ),
        (
            'Контакт',
            {'fields': ('contact_name', 'phone', 'email')},
        ),
        ('Повідомлення', {'fields': ('message',)}),
        ('Статус', {'fields': ('status',)}),
        ('Службове', {'fields': ('created_at',)}),
    )

    @admin.action(description='Статус: нова')
    def action_new(self, request, queryset):
        _bulk_set_status(self, request, queryset, PartnerApplication.Status.NEW)

    @admin.action(description='Статус: в роботі')
    def action_in_progress(self, request, queryset):
        _bulk_set_status(self, request, queryset, PartnerApplication.Status.IN_PROGRESS)

    @admin.action(description='Статус: оброблена')
    def action_done(self, request, queryset):
        _bulk_set_status(self, request, queryset, PartnerApplication.Status.DONE)

    @admin.action(description='Статус: відхилена')
    def action_rejected(self, request, queryset):
        _bulk_set_status(self, request, queryset, PartnerApplication.Status.REJECTED)

    @display(
        description='Статус',
        label={
            PartnerApplication.Status.NEW: 'info',
            PartnerApplication.Status.IN_PROGRESS: 'warning',
            PartnerApplication.Status.DONE: 'success',
            PartnerApplication.Status.REJECTED: 'danger',
        },
    )
    def status_badge(self, obj: PartnerApplication):
        return obj.status, obj.get_status_display()


@admin.register(FittingRequest)
class FittingRequestAdmin(ModelAdmin):
    list_display = (
        'name',
        'phone',
        'email',
        'product_name',
        'status_badge',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('name', 'phone', 'email', 'product_name', 'message')
    readonly_fields = ('created_at', 'product_name')
    autocomplete_fields = ('product',)
    date_hierarchy = 'created_at'
    actions = (
        'action_new',
        'action_in_progress',
        'action_done',
    )
    fieldsets = (
        ('Клієнт', {'fields': ('name', 'phone', 'email')}),
        (
            'Модель',
            {
                'description': (
                    '«Модель» — назва на момент заявки, її не змінюємо. '
                    'Поле нижче — поточний товар у каталозі; привʼязка не перезаписує snapshot.'
                ),
                'fields': ('product_name', 'product'),
            },
        ),
        ('Коментар', {'fields': ('message',)}),
        ('Статус', {'fields': ('status',)}),
        ('Службове', {'fields': ('created_at',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['product'].label = 'Товар у каталозі'
        form.base_fields['product'].help_text = (
            'Поточна картка товару. Зміна не перезаписує назву з заявки.'
        )
        return form

    @admin.action(description='Статус: нова')
    def action_new(self, request, queryset):
        _bulk_set_status(self, request, queryset, FittingRequest.Status.NEW)

    @admin.action(description='Статус: в роботі')
    def action_in_progress(self, request, queryset):
        _bulk_set_status(self, request, queryset, FittingRequest.Status.IN_PROGRESS)

    @admin.action(description='Статус: оброблена')
    def action_done(self, request, queryset):
        _bulk_set_status(self, request, queryset, FittingRequest.Status.DONE)

    @display(
        description='Статус',
        label={
            FittingRequest.Status.NEW: 'info',
            FittingRequest.Status.IN_PROGRESS: 'warning',
            FittingRequest.Status.DONE: 'success',
        },
    )
    def status_badge(self, obj: FittingRequest):
        return obj.status, obj.get_status_display()
