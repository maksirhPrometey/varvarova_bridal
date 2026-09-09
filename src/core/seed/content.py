from datetime import timedelta

from django.utils import timezone

from src.catalog.models import Product
from src.content.models import (
    AboutPage,
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
from src.content.home_models import HomePage
from src.content.landing_models import (
    CarePage,
    ContactsPage,
    DeliveryPage,
    OfferPage,
    PartnershipPage,
    PrivacyPage,
)
from src.content.stubs import (
    ABOUT_DEFAULTS,
    CARE_DEFAULTS,
    CONTACTS_DEFAULTS,
    DELIVERY_DEFAULTS,
    HOME_DEFAULTS,
    OFFER_DEFAULTS,
    PARTNERSHIP_DEFAULTS,
    PRIVACY_DEFAULTS,
)
from src.core.seed.images import render_banner, render_cover, replace_image

FAQ = [
    ('Як записатися на примірку?', 'Залиште заявку в контактах або зателефонуйте в салон. Примірка триває близько години, з собою варто взяти взуття на каблуку.'),
    ('Чи можна пошити за власними мірками?', 'Так. Більшість суконь шиємо індивідуально після першої примірки. Термін — 6–10 тижнів залежно від декору.'),
    ('Які розміри є в наявності?', 'У салоні стоїть зразок для примірки. Фінальна сукня — за вашими мірками. На складі кілька моделей у стандартних розмірах.'),
    ('Як відбувається доставка?', 'Нова Пошта або курʼєр у Львові. Самовивіз із салону безкоштовний. Міжнародні відправки узгоджуємо окремо.'),
    ('Чи можна повернути сукню?', 'Індивідуальний пошив не підлягає поверненню. Моделі зі складу — протягом 14 днів у товарному вигляді, без слідів примірки на заході.'),
]

BLOG = [
    (
        'prymirka-u-lvovi',
        'Як підготуватися до примірки',
        'Взуття, білизна і спокійний графік — коротко про те, що реально допомагає обрати сукню.',
        'Приходьте з взуттям, близьким до весільного каблука. Візьміть одну близьку людину, не групу. '
        'Ми починаємо з силуету, далі — тканина і декор. Так легше не загубитися в деталях.',
        'ivory',
    ),
    (
        'tkanyny-sezonu',
        'Мікадо, креп і фатин цього сезону',
        'Чим відрізняються три основні тканини колекції і для якої церемонії яка сідає краще.',
        'Мікадо тримає архітектуру пишного силуету. Креп — для сучасного футляра. '
        'Фатин дає повітря A-силуету. У салоні покажемо зразки на світлі зали.',
        'champagne',
    ),
]

SITE_CONTACTS = {
    'phone': '+380322000100',
    'email': 'hello@varvarova.com',
    'instagram': 'https://instagram.com/varvarova',
    'address': 'Львів, вул. Січових Стрільців, 12',
    'bank': {
        'recipient': 'ФОП Варварова',
        'iban': 'UA123456789012345678901234567',
        'edrpou': '12345678',
        'bank_name': 'ПриватБанк',
    },
}

SALONS = [
    {
        'name': 'VARVAROVA',
        'country': 'Україна',
        'city': 'Ірпінь',
        'address': 'Ірпінь, Київська область',
        'phone': '+380322000100',
        'email': 'hello@varvarova.com',
        'lat': '50.518600',
        'lng': '30.241700',
        'working_hours': 'Вт–Сб 11:00–19:00 · Нд за записом',
        'sort_order': 10,
    },
]

TRUNK_SHOWS = [
    (
        'Trunk Show — Milano',
        'Мілан',
        'Brera Atelier',
        21,
        'Показ весільної лінії та couture для партнерів Італії.',
    ),
    (
        'Trunk Show — Paris',
        'Париж',
        'Rue de Turenne',
        45,
        'Примірка нової колекції для салонів Франції.',
    ),
]

REVIEWS = [
    ('Марія, Львів', 'Aurelia сіла з першої примірки. Мереживо мʼяке, шлейф не заважав у залі.', 5, 'aurelia'),
    ('Олена, Київ', 'Celeste — саме той сучасний крій, який хотіла. Пошив за мірками без зайвих сюрпризів.', 5, 'celeste'),
    ('Ірина, Івано-Франківськ', 'Isadora важка, але тримає форму весь вечір. Дякуємо ательє за терпіння з декором.', 5, 'isadora'),
    ('Анна, Варшава', 'Nocturne брала на вечірку бренду. Креп не мнеться, вигляд дорогий.', 4, 'nocturne'),
]


def seed_content() -> dict[str, int]:
    settings = SiteSettings.load()
    settings.site_name = 'Varvarova'
    settings.contacts_json = dict(SITE_CONTACTS)
    settings.robots_txt = 'User-agent: *\nAllow: /\n'
    settings.save()

    home, _home_created = HomePage.objects.update_or_create(
        pk=1,
        defaults={
            **HOME_DEFAULTS,
            'seo_title': 'Varvarova',
        },
    )
    replace_image(home.hero_image, 'hero.jpg', render_banner())
    AboutPage.objects.update_or_create(
        pk=1,
        defaults={
            **ABOUT_DEFAULTS,
            'seo_title': 'Про бренд — Varvarova',
        },
    )
    Page.objects.filter(slug='about').delete()
    partner, _created = PartnershipPage.objects.update_or_create(
        pk=1,
        defaults={
            **PARTNERSHIP_DEFAULTS,
            'seo_title': 'Стати партнером — Varvarova',
        },
    )
    if not partner.hero_image:
        replace_image(partner.hero_image, 'hero.jpg', render_cover('Партнерам', 'ivory'))
    Page.objects.filter(slug='partnership').delete()
    DeliveryPage.objects.update_or_create(
        pk=1,
        defaults={
            **DELIVERY_DEFAULTS,
            'seo_title': 'Доставка та оплата — Varvarova',
        },
    )
    Page.objects.filter(slug='delivery').delete()
    CarePage.objects.update_or_create(
        pk=1,
        defaults={
            **CARE_DEFAULTS,
            'seo_title': 'Догляд за сукнею — Varvarova',
        },
    )
    Page.objects.filter(slug='care').delete()
    OfferPage.objects.update_or_create(
        pk=1,
        defaults={
            **OFFER_DEFAULTS,
            'seo_title': 'Публічна оферта — Varvarova',
        },
    )
    Page.objects.filter(slug='offer').delete()
    PrivacyPage.objects.update_or_create(
        pk=1,
        defaults={
            **PRIVACY_DEFAULTS,
            'seo_title': 'Політика конфіденційності — Varvarova',
        },
    )
    Page.objects.filter(slug='privacy').delete()
    ContactsPage.objects.update_or_create(
        pk=1,
        defaults={
            **CONTACTS_DEFAULTS,
            'seo_title': 'Контакти — Varvarova',
        },
    )
    Page.objects.filter(slug='contacts').delete()

    for index, (question, answer) in enumerate(FAQ):
        FaqItem.objects.update_or_create(
            question=question,
            defaults={'answer': answer, 'sort_order': index, 'is_published': True},
        )

    now = timezone.now()
    for index, (slug, title, excerpt, body, tone) in enumerate(BLOG):
        post, created = BlogPost.objects.update_or_create(
            slug=slug,
            defaults={
                'title': title,
                'excerpt': excerpt,
                'body': body,
                'published_at': now - timedelta(days=7 * (index + 1)),
                'is_published': True,
                'seo_title': f'{title} — Varvarova',
            },
        )
        if created or not post.cover_image:
            replace_image(post.cover_image, f'{slug}.jpg', render_cover(title, tone))

    kept_ids = []
    for row in SALONS:
        salon, _ = Salon.objects.update_or_create(
            name=row['name'],
            city=row['city'],
            defaults={**{k: v for k, v in row.items() if k not in ('name', 'city')}, 'is_active': True},
        )
        kept_ids.append(salon.pk)
    Salon.objects.exclude(pk__in=kept_ids).update(is_active=False)

    for title, city, place, days, description in TRUNK_SHOWS:
        TrunkShow.objects.update_or_create(
            title=title,
            defaults={
                'home_page': home,
                'city': city,
                'place': place,
                'starts_at': now + timedelta(days=days),
                'ends_at': now + timedelta(days=days + 2),
                'description': description,
                'is_published': True,
            },
        )

    products = {p.slug: p for p in Product.objects.filter(slug__in=['aurelia', 'celeste', 'isadora', 'nocturne'])}
    for index, (author, text, rating, slug) in enumerate(REVIEWS):
        Review.objects.update_or_create(
            author_name=author,
            product=products.get(slug),
            defaults={'text': text, 'rating': rating, 'is_published': True, 'sort_order': index},
        )

    for index, slug in enumerate(('aurelia', 'odette', 'elara')):
        product = products.get(slug) or Product.objects.filter(slug=slug).first()
        if product is None:
            continue
        item, created = BrideGalleryItem.objects.update_or_create(
            title=f'Наречена в {product.name}',
            defaults={'product': product, 'sort_order': index, 'is_published': True},
        )
        if created or not item.image:
            replace_image(
                item.image,
                f'bride-{slug}.jpg',
                render_cover(product.name, 'ivory'),
            )

    PartnerApplication.objects.get_or_create(
        email='salon.odesa@example.com',
        defaults={
            'company_name': 'Atelier Odesa',
            'contact_name': 'Катерина Литвин',
            'phone': '+380487001122',
            'city': 'Одеса',
            'message': 'Шукаємо ексклюзив по Одесі на весільну лінію.',
            'status': PartnerApplication.Status.NEW,
        },
    )

    return {
        'pages': Page.objects.filter(is_published=True).count(),
        'faq': FaqItem.objects.filter(is_published=True).count(),
        'salons': Salon.objects.filter(is_active=True).count(),
    }
