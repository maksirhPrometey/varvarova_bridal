from src.catalog.selectors import root_catalog_categories
from src.content.selectors import site_settings


def storefront(request):
    settings_obj = site_settings()
    roots = {c.slug: c for c in root_catalog_categories()}
    return {
        'site_settings': settings_obj,
        'nav_wedding': roots.get('wedding'),
        'nav_evening': roots.get('evening'),
        'nav_accessories': roots.get('accessories'),
        'nav_lingerie': roots.get('lingerie'),
    }
