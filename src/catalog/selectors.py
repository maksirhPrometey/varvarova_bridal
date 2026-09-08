from django.db.models import QuerySet

from src.catalog.models import Attribute, Category, Product, ProductAttributeValue, WishlistItem
from src.catalog.product_grid import pick_grid_columns
from src.users.models import User

MAX_WISHLIST_IDS = 80

SORT_NEW = 'new'
SORT_PRICE_ASC = 'price_asc'
SORT_PRICE_DESC = 'price_desc'
SORT_MANUAL = 'manual'
SORT_CHOICES = (SORT_NEW, SORT_PRICE_ASC, SORT_PRICE_DESC, SORT_MANUAL)

SORT_MAP = {
    SORT_NEW: ('-created_at', 'id'),
    SORT_PRICE_ASC: ('price_uah', 'id'),
    SORT_PRICE_DESC: ('-price_uah', 'id'),
    SORT_MANUAL: ('sort_order', 'id'),
}


def active_products() -> QuerySet[Product]:
    return (
        Product.objects.filter(is_active=True)
        .select_related('category')
        .prefetch_related('images')
    )


def featured_products(*, limit: int = 8) -> list[Product]:
    return list(
        active_products().filter(is_featured=True).order_by('sort_order', '-created_at')[:limit]
    )


_EVENING_SHOT_SLUGS = ('atelier-ivoire', 'atelier-emeraude')


def evening_home_shots(*, limit: int = 2) -> list[Product]:
    preferred = {
        product.slug: product
        for product in active_products().filter(slug__in=_EVENING_SHOT_SLUGS)
    }
    shots = [preferred[slug] for slug in _EVENING_SHOT_SLUGS if slug in preferred]
    if len(shots) >= limit:
        return shots[:limit]
    couture = category_by_slug('evening-couture')
    if couture is not None:
        extra = list(
            active_products()
            .filter(category=couture)
            .exclude(pk__in=[item.pk for item in shots])
            .order_by('sort_order', 'id')[: limit - len(shots)]
        )
        shots.extend(extra)
        if len(shots) >= limit:
            return shots[:limit]
    evening = category_by_slug('evening')
    if evening is None:
        return shots[:limit]
    extra = list(
        filter_catalog(evening, sort=SORT_MANUAL).exclude(pk__in=[item.pk for item in shots])[
            : limit - len(shots)
        ]
    )
    return (shots + extra)[:limit]


def root_catalog_categories() -> list[Category]:
    return list(
        Category.objects.filter(parent__isnull=True, is_active=True).order_by(
            'sort_order', 'name'
        )
    )


def category_is_public(category: Category) -> bool:
    current = category
    seen: set[int] = set()
    while current is not None:
        if current.pk in seen:
            return False
        seen.add(current.pk)
        if not current.is_active:
            return False
        current = current.parent
    return True


def category_by_slug(slug: str) -> Category | None:
    category = (
        Category.objects.filter(slug=slug, is_active=True)
        .select_related('parent')
        .first()
    )
    if category is None or not category_is_public(category):
        return None
    return category


def category_subtree_ids(category: Category) -> list[int]:
    ids = [category.id]
    children = Category.objects.filter(parent=category, is_active=True)
    for child in children:
        ids.extend(category_subtree_ids(child))
    return ids


def category_ancestors(category: Category) -> list[Category]:
    """Батьки від кореня до безпосереднього parent (без самої категорії)."""
    chain: list[Category] = []
    current = category.parent
    seen: set[int] = set()
    while current is not None:
        if current.pk in seen:
            break
        seen.add(current.pk)
        chain.append(current)
        current = current.parent
    chain.reverse()
    return chain


def parse_filter_query(query) -> dict[str, set[str]]:
    selected: dict[str, set[str]] = {}
    for raw in query.getlist('a'):
        if '=' not in raw:
            continue
        code, slug = raw.split('=', 1)
        code = code.strip()
        slug = slug.strip()
        if not code or not slug:
            continue
        selected.setdefault(code, set()).add(slug)
    return selected


def apply_sort(qs: QuerySet[Product], sort: str) -> QuerySet[Product]:
    if sort not in SORT_CHOICES:
        sort = SORT_NEW
    return qs.order_by(*SORT_MAP[sort])


def filter_catalog(
    category: Category,
    *,
    selected: dict[str, set[str]] | None = None,
    sort: str = SORT_NEW,
) -> QuerySet[Product]:
    ids = category_subtree_ids(category)
    qs = active_products().filter(category_id__in=ids)
    selected = selected or {}
    for code, slugs in selected.items():
        qs = qs.filter(
            attribute_values__attribute_value__attribute__code=code,
            attribute_values__attribute_value__slug__in=slugs,
        )
    qs = qs.distinct()
    return apply_sort(qs, sort)


def catalog_facets(category: Category) -> list[dict]:
    ids = category_subtree_ids(category)
    value_ids = (
        ProductAttributeValue.objects.filter(
            product__is_active=True,
            product__category_id__in=ids,
            attribute_value__attribute__filterable=True,
        )
        .values_list('attribute_value_id', flat=True)
        .distinct()
    )
    attributes = (
        Attribute.objects.filter(filterable=True, values__id__in=value_ids)
        .prefetch_related('values')
        .distinct()
        .order_by('sort_order', 'id')
    )
    facets = []
    value_id_set = set(value_ids)
    for attribute in attributes:
        values = [v for v in attribute.values.all() if v.id in value_id_set]
        if not values:
            continue
        values.sort(key=lambda v: (v.sort_order, v.id))
        facets.append({'attribute': attribute, 'values': values})
    return facets


def product_by_slug(slug: str) -> Product | None:
    product = (
        active_products()
        .prefetch_related('attribute_values__attribute_value__attribute')
        .filter(slug=slug)
        .first()
    )
    if product is None:
        return None
    if not category_is_public(product.category):
        return None
    return product


def parse_wishlist_ids(raw) -> list[int]:
    if raw is None:
        parts: list = []
    elif isinstance(raw, (list, tuple)):
        parts = list(raw)
    else:
        parts = str(raw).split(',')
    seen: set[int] = set()
    ids: list[int] = []
    for part in parts:
        try:
            value = int(part)
        except (TypeError, ValueError):
            continue
        if value < 1 or value in seen:
            continue
        seen.add(value)
        ids.append(value)
        if len(ids) >= MAX_WISHLIST_IDS:
            break
    return ids


def active_products_by_ids(ids: list[int]) -> list[Product]:
    if not ids:
        return []
    found = {
        p.id: p
        for p in active_products().filter(pk__in=ids)
    }
    return [found[i] for i in ids if i in found]


def wishlist_products_for_user(user: User) -> list[Product]:
    items = (
        WishlistItem.objects.filter(user=user, product__is_active=True)
        .select_related('product', 'product__category')
        .prefetch_related('product__images')
        .order_by('-created_at', '-id')
    )
    return [item.product for item in items]


def wishlist_product_ids_for_user(user: User) -> list[int]:
    return list(
        WishlistItem.objects.filter(user=user).values_list('product_id', flat=True)
    )


def grid_cols_for(count: int) -> int:
    return pick_grid_columns(count)


def gallery_rows(images: list) -> list[dict]:
    if not images:
        return []
    if len(images) == 1:
        return [{'kind': 'full', 'images': [images[0]]}]
    if len(images) == 2:
        return [{'kind': 'pair', 'images': list(images)}]
    rows = [{'kind': 'full', 'images': [images[0]]}]
    rest = images[1:]
    index = 0
    while index < len(rest):
        pair = rest[index:index + 2]
        rows.append({'kind': 'pair' if len(pair) == 2 else 'full', 'images': pair})
        index += 2
    return rows


def filter_chips(request, facets: list[dict]) -> list[dict]:
    chips = []
    for facet in facets:
        for value in facet['values']:
            if not value['checked']:
                continue
            params = request.GET.copy()
            kept = [item for item in params.getlist('a') if item != value['query']]
            params.setlist('a', kept)
            query = params.urlencode()
            chips.append(
                {
                    'label': f"{facet['attribute'].name}: {value['obj'].value}",
                    'href': f'?{query}' if query else request.path,
                }
            )
    return chips
