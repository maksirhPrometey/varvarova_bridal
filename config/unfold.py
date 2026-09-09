from django.urls import reverse_lazy


def _has(perm: str):
    return lambda request, _perm=perm: request.user.has_perm(_perm)


def _is_superuser(request):
    return request.user.is_superuser


def _can_see_catalog(request):
    return request.user.has_perm('catalog.change_product') or request.user.has_perm(
        'commerce.view_order'
    )


def admin_navigation(request):
    sections = (
        {
            'title': 'Каталог',
            'separator': False,
            'items': [
                {
                    'title': 'Товари',
                    'icon': 'checkroom',
                    'link': reverse_lazy('admin:catalog_product_changelist'),
                    'permission': _can_see_catalog,
                },
                {
                    'title': 'Категорії',
                    'icon': 'category',
                    'link': reverse_lazy('admin:catalog_category_changelist'),
                    'permission': _can_see_catalog,
                },
                {
                    'title': 'Фільтри',
                    'icon': 'tune',
                    'link': reverse_lazy('admin:catalog_attribute_changelist'),
                    'permission': _can_see_catalog,
                },
                {
                    'title': 'Значення фільтрів',
                    'icon': 'label',
                    'link': reverse_lazy('admin:catalog_attributevalue_changelist'),
                    'permission': _can_see_catalog,
                },
            ],
        },
        {
            'title': 'Продажі',
            'separator': True,
            'items': [
                {
                    'title': 'Замовлення',
                    'icon': 'receipt_long',
                    'link': reverse_lazy('admin:commerce_order_changelist'),
                    'permission': _has('commerce.view_order'),
                },
                {
                    'title': 'Кошики',
                    'icon': 'shopping_cart',
                    'link': reverse_lazy('admin:commerce_cart_changelist'),
                    'permission': _has('commerce.view_cart'),
                },
                {
                    'title': 'Улюблене',
                    'icon': 'favorite',
                    'link': reverse_lazy('admin:catalog_wishlistitem_changelist'),
                    'permission': _has('catalog.view_wishlistitem'),
                },
                {
                    'title': 'Заявки на примірку',
                    'icon': 'event_available',
                    'link': reverse_lazy('admin:content_fittingrequest_changelist'),
                    'permission': _has('content.view_fittingrequest'),
                },
                {
                    'title': 'Заявки партнерів',
                    'icon': 'handshake',
                    'link': reverse_lazy('admin:content_partnerapplication_changelist'),
                    'permission': _has('content.view_partnerapplication'),
                },
            ],
        },
        {
            'title': 'Контент',
            'separator': True,
            'items': [
                {
                    'title': 'Головна',
                    'icon': 'home',
                    'link': reverse_lazy('admin:content_homepage_changelist'),
                    'permission': _has('content.view_homepage'),
                },
                {
                    'title': 'Налаштування сайту',
                    'icon': 'settings',
                    'link': reverse_lazy('admin:content_sitesettings_changelist'),
                    'permission': _has('content.change_sitesettings'),
                },
                {
                    'title': 'Про бренд',
                    'icon': 'auto_stories',
                    'link': reverse_lazy('admin:content_aboutpage_changelist'),
                    'permission': _has('content.view_aboutpage'),
                },
                {
                    'title': 'Партнерам',
                    'icon': 'groups',
                    'link': reverse_lazy('admin:content_partnershippage_changelist'),
                    'permission': _has('content.view_partnershippage'),
                },
                {
                    'title': 'Доставка',
                    'icon': 'local_shipping',
                    'link': reverse_lazy('admin:content_deliverypage_changelist'),
                    'permission': _has('content.view_deliverypage'),
                },
                {
                    'title': 'Догляд',
                    'icon': 'dry_cleaning',
                    'link': reverse_lazy('admin:content_carepage_changelist'),
                    'permission': _has('content.view_carepage'),
                },
                {
                    'title': 'Оферта',
                    'icon': 'gavel',
                    'link': reverse_lazy('admin:content_offerpage_changelist'),
                    'permission': _has('content.view_offerpage'),
                },
                {
                    'title': 'Політика',
                    'icon': 'policy',
                    'link': reverse_lazy('admin:content_privacypage_changelist'),
                    'permission': _has('content.view_privacypage'),
                },
                {
                    'title': 'Контакти',
                    'icon': 'call',
                    'link': reverse_lazy('admin:content_contactspage_changelist'),
                    'permission': _has('content.view_contactspage'),
                },
                {
                    'title': 'Блог',
                    'icon': 'newspaper',
                    'link': reverse_lazy('admin:content_blogpost_changelist'),
                    'permission': _has('content.view_blogpost'),
                },
                {
                    'title': 'FAQ',
                    'icon': 'help',
                    'link': reverse_lazy('admin:content_faqitem_changelist'),
                    'permission': _has('content.view_faqitem'),
                },
                {
                    'title': 'Відгуки',
                    'icon': 'reviews',
                    'link': reverse_lazy('admin:content_review_changelist'),
                    'permission': _has('content.view_review'),
                },
                {
                    'title': 'Салони',
                    'icon': 'store',
                    'link': reverse_lazy('admin:content_salon_changelist'),
                    'permission': _has('content.view_salon'),
                },
                {
                    'title': 'Наречені',
                    'icon': 'photo_camera',
                    'link': reverse_lazy('admin:content_bridegalleryitem_changelist'),
                    'permission': _has('content.view_bridegalleryitem'),
                },
            ],
        },
        {
            'title': 'Користувачі',
            'separator': True,
            'items': [
                {
                    'title': 'Користувачі',
                    'icon': 'person',
                    'link': reverse_lazy('admin:users_user_changelist'),
                    'permission': _is_superuser,
                },
                {
                    'title': 'Групи',
                    'icon': 'group',
                    'link': reverse_lazy('admin:auth_group_changelist'),
                    'permission': _is_superuser,
                },
            ],
        },
    )
    visible = []
    for section in sections:
        items = [item for item in section['items'] if item['permission'](request)]
        if not items:
            continue
        visible.append({**section, 'items': items})
    return visible


UNFOLD = {
    'SITE_TITLE': 'Varvarova',
    'SITE_HEADER': 'Varvarova — Адмінпанель',
    'SITE_SYMBOL': 'checkroom',
    'SIDEBAR': {
        'show_search': True,
        'command_search': True,
        'show_all_applications': False,
        'navigation': admin_navigation,
    },
}
