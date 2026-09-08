from django.utils import timezone

from src.catalog.selectors import evening_home_shots, featured_products, root_catalog_categories
from src.content.models import (
    Banner,
    BlogPost,
    BrideGalleryItem,
    FaqItem,
    Page,
    Review,
    Salon,
    SiteSettings,
    TrunkShow,
)

PAGE_SLUGS = frozenset({'about', 'delivery', 'care', 'offer', 'privacy'})


def site_settings() -> SiteSettings:
    return SiteSettings.load()


def active_banners():
    return Banner.objects.filter(is_active=True).order_by('sort_order', 'id')


def published_trunk_shows():
    return TrunkShow.objects.filter(is_published=True).order_by('-starts_at')


def upcoming_trunk_shows():
    now = timezone.now()
    return published_trunk_shows().filter(starts_at__gte=now)


def published_page(slug: str) -> Page | None:
    return Page.objects.filter(slug=slug, is_published=True).first()


def published_faq():
    return FaqItem.objects.filter(is_published=True).order_by('sort_order', 'id')


def published_blog_posts():
    now = timezone.now()
    return (
        BlogPost.objects.filter(is_published=True)
        .exclude(published_at__gt=now)
        .order_by('-published_at', '-id')
    )


def published_blog_post(slug: str) -> BlogPost | None:
    return published_blog_posts().filter(slug=slug).first()


def published_reviews():
    return (
        Review.objects.filter(is_published=True)
        .select_related('product')
        .order_by('sort_order', '-created_at')
    )


def active_salons():
    return Salon.objects.filter(is_active=True).order_by('sort_order', 'id')


def published_brides():
    return (
        BrideGalleryItem.objects.filter(is_published=True)
        .select_related('product')
        .order_by('sort_order', 'id')
    )


def home_context() -> dict:
    featured = featured_products(limit=8)
    upcoming = list(upcoming_trunk_shows()[:6])
    trunk_shows = upcoming if upcoming else list(published_trunk_shows()[:6])
    return {
        'page_title': site_settings().site_name,
        'banners': list(active_banners()),
        'featured_products': featured,
        'featured_grid_cols': pick_home_cols(len(featured)),
        'evening_shots': evening_home_shots(limit=2),
        'trunk_shows': trunk_shows,
        'root_categories': root_catalog_categories(),
    }


def pick_home_cols(count: int) -> int:
    from src.catalog.product_grid import pick_grid_columns

    return pick_grid_columns(count)


def resolve_title(obj, fallback: str) -> str:
    seo = getattr(obj, 'seo_title', None)
    if seo:
        return seo
    for attr in ('title', 'name'):
        value = getattr(obj, attr, None)
        if value:
            return value
    return fallback
