from django.urls import reverse_lazy

UNFOLD = {
    'SITE_TITLE': 'Varvarova',
    'SITE_HEADER': 'Varvarova — Адмінпанель',
    'SITE_SYMBOL': 'checkroom',
    'SIDEBAR': {
        'show_search': True,
        'command_search': True,
        'show_all_applications': False,
        'navigation': [
            {
                'title': 'Каталог',
                'separator': False,
                'items': [
                    {
                        'title': 'Товари',
                        'icon': 'checkroom',
                        'link': reverse_lazy('admin:catalog_product_changelist'),
                    },
                    {
                        'title': 'Категорії',
                        'icon': 'category',
                        'link': reverse_lazy('admin:catalog_category_changelist'),
                    },
                    {
                        'title': 'Фільтри',
                        'icon': 'tune',
                        'link': reverse_lazy('admin:catalog_attribute_changelist'),
                    },
                    {
                        'title': 'Значення фільтрів',
                        'icon': 'label',
                        'link': reverse_lazy('admin:catalog_attributevalue_changelist'),
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
                    },
                    {
                        'title': 'Кошики',
                        'icon': 'shopping_cart',
                        'link': reverse_lazy('admin:commerce_cart_changelist'),
                    },
                    {
                        'title': 'Обране',
                        'icon': 'favorite',
                        'link': reverse_lazy('admin:catalog_wishlistitem_changelist'),
                    },
                ],
            },
            {
                'title': 'Контент',
                'separator': True,
                'items': [
                    {
                        'title': 'Налаштування сайту',
                        'icon': 'settings',
                        'link': reverse_lazy('admin:content_sitesettings_changelist'),
                    },
                    {
                        'title': 'Сторінки',
                        'icon': 'article',
                        'link': reverse_lazy('admin:content_page_changelist'),
                    },
                    {
                        'title': 'Банери',
                        'icon': 'image',
                        'link': reverse_lazy('admin:content_banner_changelist'),
                    },
                    {
                        'title': 'Trunk-show',
                        'icon': 'event',
                        'link': reverse_lazy('admin:content_trunkshow_changelist'),
                    },
                    {
                        'title': 'Блог',
                        'icon': 'newspaper',
                        'link': reverse_lazy('admin:content_blogpost_changelist'),
                    },
                    {
                        'title': 'FAQ',
                        'icon': 'help',
                        'link': reverse_lazy('admin:content_faqitem_changelist'),
                    },
                    {
                        'title': 'Відгуки',
                        'icon': 'reviews',
                        'link': reverse_lazy('admin:content_review_changelist'),
                    },
                    {
                        'title': 'Салони',
                        'icon': 'store',
                        'link': reverse_lazy('admin:content_salon_changelist'),
                    },
                    {
                        'title': 'Наречені',
                        'icon': 'photo_camera',
                        'link': reverse_lazy('admin:content_bridegalleryitem_changelist'),
                    },
                    {
                        'title': 'Заявки партнерів',
                        'icon': 'handshake',
                        'link': reverse_lazy('admin:content_partnerapplication_changelist'),
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
                    },
                    {
                        'title': 'Групи',
                        'icon': 'group',
                        'link': reverse_lazy('admin:auth_group_changelist'),
                    },
                ],
            },
        ],
    },
}
