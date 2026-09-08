from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.html import format_html
from unfold.admin import ModelAdmin
from unfold.decorators import display

from src.content.models import (
    Banner,
    BlogPost,
    BrideGalleryItem,
    FaqItem,
    Page,
    PartnerApplication,
    Review,
    Salon,
    SiteSettings,
    TrunkShow,
)
from src.core.admin import TinyMCEAdminMixin


@admin.register(SiteSettings)
class SiteSettingsAdmin(ModelAdmin):
    readonly_fields = ('logo_preview', 'updated_at')
    fieldsets = (
        (None, {'fields': ('site_name', 'logo', 'logo_preview')}),
        ('Контакти', {'fields': ('contacts_json',)}),
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


@admin.register(Page)
class PageAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('body',)
    list_display = ('title', 'slug', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'slug')
    list_editable = ('is_published',)
    prepopulated_fields = {'slug': ('title',)}


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

    @display(description='Фото', image=True)
    def cover_thumb(self, obj: BlogPost):
        return obj.cover_image.url if obj.cover_image else None

    def cover_preview(self, obj):
        if obj and obj.cover_image:
            return format_html(
                '<img src="{}" alt="" width="160" height="160">',
                obj.cover_image.url,
            )
        return '—'

    cover_preview.short_description = 'Превʼю'


@admin.register(Review)
class ReviewAdmin(ModelAdmin):
    list_display = ('author_name', 'rating', 'product', 'is_published', 'sort_order')
    list_filter = ('is_published', 'rating')
    search_fields = ('author_name', 'text')
    list_editable = ('is_published', 'sort_order')
    autocomplete_fields = ('product',)
    readonly_fields = ('created_at',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(Salon)
class SalonAdmin(ModelAdmin):
    list_display = ('name', 'city', 'phone', 'is_active', 'sort_order')
    list_filter = ('is_active', 'country', 'city')
    search_fields = ('name', 'city', 'address', 'phone')
    list_editable = ('is_active', 'sort_order')


@admin.register(Banner)
class BannerAdmin(ModelAdmin):
    list_display = ('thumb', 'title', 'is_active', 'sort_order')
    list_display_links = ('thumb', 'title')
    list_filter = ('is_active',)
    list_editable = ('is_active', 'sort_order')
    search_fields = ('title', 'link_url')
    readonly_fields = ('image_preview',)
    fields = ('title', 'image', 'image_preview', 'link_url', 'sort_order', 'is_active')

    @display(description='Фото', image=True)
    def thumb(self, obj: Banner):
        return obj.image.url if obj.image else None

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html('<img src="{}" alt="" width="240" height="120">', obj.image.url)
        return '—'

    image_preview.short_description = 'Превʼю'


@admin.register(TrunkShow)
class TrunkShowAdmin(TinyMCEAdminMixin, ModelAdmin):
    tinymce_fields = ('description',)
    list_display = ('title', 'city', 'starts_at', 'is_published')
    list_filter = ('is_published',)
    search_fields = ('title', 'city', 'place')
    list_editable = ('is_published',)
    date_hierarchy = 'starts_at'


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

    @display(description='Фото', image=True)
    def thumb(self, obj: BrideGalleryItem):
        return obj.image.url if obj.image else None

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
        'email',
        'city',
        'status_badge',
        'created_at',
    )
    list_filter = ('status',)
    search_fields = ('company_name', 'contact_name', 'email', 'phone', 'city')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'

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
        return obj.status
