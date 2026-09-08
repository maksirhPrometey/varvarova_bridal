from decimal import Decimal

from src.catalog.models import (
    Attribute,
    AttributeValue,
    Category,
    Product,
    ProductAttributeValue,
    ProductImage,
)
from src.core.seed.catalog_data import ATTRIBUTES, CATEGORIES, PRODUCTS
from src.core.seed.images import as_file, render_portrait

_SHOT_ALTS = (
    '{name} — фас',
    '{name} — деталь',
    '{name} — спина',
    '{name} — профіль',
)


def _ensure_gallery(product: Product, name: str, tone: str) -> None:
    if product.images.count() == 4:
        return
    for old in product.images.all():
        if old.image:
            old.image.delete(save=False)
        old.delete()
    for index, alt in enumerate(_SHOT_ALTS):
        shot = ProductImage(
            product=product,
            alt=alt.format(name=name),
            sort_order=index,
            is_main=index == 0,
        )
        filename = f'{product.slug}-{index + 1}.jpg'
        shot.image.save(
            filename,
            as_file(render_portrait(name, tone, variant=index), filename),
            save=True,
        )


def _short(name: str, category_name: str) -> str:
    return f'{name} — {category_name.lower()} ательє Varvarova. Пошив у Львові.'


def _body(name: str, values: dict[str, AttributeValue]) -> str:
    silhouette = values['silhouette'].value
    fabric = values['fabric'].value
    color = values['color'].value
    return (
        f'{name} створена в ательє Varvarova у Львові. '
        f'Силует {silhouette.lower()}, тканина — {fabric.lower()}, колір {color.lower()}. '
        'Сукня сідає за індивідуальними мірками. '
        'Примірка в салоні або через запис на trunk-show.'
    )


def seed_catalog() -> dict[str, int]:
    categories: dict[str, Category] = {}
    for row in CATEGORIES:
        parent = categories[row['parent']] if row['parent'] else None
        category, _ = Category.objects.update_or_create(
            slug=row['slug'],
            defaults={
                'name': row['name'],
                'parent': parent,
                'description': row['description'],
                'sort_order': row['sort_order'],
                'is_active': True,
                'seo_title': f'{row["name"]} — Varvarova',
            },
        )
        categories[row['slug']] = category

    values: dict[tuple[str, str], AttributeValue] = {}
    for code, name, sort_order, options in ATTRIBUTES:
        attribute, _ = Attribute.objects.update_or_create(
            code=code,
            defaults={'name': name, 'filterable': True, 'sort_order': sort_order},
        )
        for index, (slug, label) in enumerate(options):
            value, _ = AttributeValue.objects.update_or_create(
                attribute=attribute,
                slug=slug,
                defaults={'value': label, 'sort_order': index},
            )
            values[(code, slug)] = value

    created_products = 0
    for index, (sku, slug, name, cat_slug, price, stock, featured, tone, attrs) in enumerate(PRODUCTS):
        category = categories[cat_slug]
        product, created = Product.objects.update_or_create(
            sku=sku,
            defaults={
                'slug': slug,
                'name': name,
                'category': category,
                'short_description': _short(name, category.name),
                'description': _body(name, {key: values[(key, val)] for key, val in attrs.items()}),
                'price_uah': Decimal(price),
                'stock_qty': stock,
                'is_active': True,
                'is_featured': featured,
                'sort_order': index,
                'seo_title': f'{name} — Varvarova',
            },
        )
        if created:
            created_products += 1
        for code, val_slug in attrs.items():
            ProductAttributeValue.objects.get_or_create(
                product=product,
                attribute_value=values[(code, val_slug)],
            )
        _ensure_gallery(product, name, tone)

    return {
        'categories': Category.objects.count(),
        'products': Product.objects.count(),
        'products_created': created_products,
    }
