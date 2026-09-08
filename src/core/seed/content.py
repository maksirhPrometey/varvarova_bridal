from datetime import timedelta

from django.utils import timezone

from src.catalog.models import Product
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
from src.core.seed.images import as_file, render_banner, render_cover

PAGES = [
    (
        'about',
        'Про бренд',
        'Varvarova — львівське ательє весільних і вечірніх суконь. '
        'Кожну модель збираємо вручну: від лекал до фінальної примірки. '
        'Працюємо з салонами в Україні та за кордоном, зберігаючи єдиний стандарт посадки.',
    ),
    (
        'delivery',
        'Доставка і примірка',
        'Доставка Новою Поштою по Україні або курʼєром у Львові. '
        'Самовивіз із салону на вул. Січових Стрільців. '
        'Весільні сукні пакуємо в чохол. Міжнародна відправка — за запитом менеджера.',
    ),
    (
        'care',
        'Догляд за сукнею',
        'Зберігайте сукню в чохлі, далеко від прямого сонця. '
        'Чистка — лише в ательє або спеціалізованому сервісі. '
        'Не відпарюйте мереживо парою впритул. Після церемонії рекомендуємо професійну консервацію.',
    ),
    (
        'offer',
        'Публічна оферта',
        'Цей текст є публічною офертою магазину Varvarova. '
        'Замовляючи сукню, ви підтверджуєте згоду з умовами оплати, доставки та повернення, '
        'описаними на цій сторінці та в листуванні з менеджером.',
    ),
    (
        'privacy',
        'Політика конфіденційності',
        'Ми зберігаємо імʼя, телефон і email лише для замовлення та запису на примірку. '
        'Дані не передаємо третім сторонам, окрім служби доставки та платіжного сервісу.',
    ),
    (
        'contacts',
        'Контакти',
        'Салон і виробництво: Львів. Запис на примірку — за телефоном або формою на сайті. '
        'Для оптових запитів пишіть на сторінку партнерства.',
    ),
    (
        'partnership',
        'Стати партнером',
        'Понад 400 салонів працюють з Varvarova напряму з виробництва у Львові. '
        'Партнер отримує оптовий прайс, закріплену територію та кампейн-матеріали колекції.',
    ),
]

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

SALONS = [
    {
        'name': 'Varvarova Atelier',
        'country': 'Україна',
        'city': 'Львів',
        'address': 'вул. Січових Стрільців, 12',
        'phone': '+380322000100',
        'email': 'lviv@varvarova.com',
        'lat': '49.841000',
        'lng': '24.031500',
        'working_hours': 'Вт–Сб 11:00–19:00',
        'sort_order': 10,
    },
    {
        'name': 'Varvarova Kyiv Salon',
        'country': 'Україна',
        'city': 'Київ',
        'address': 'вул. Велика Васильківська, 48',
        'phone': '+380442000200',
        'email': 'kyiv@varvarova.com',
        'lat': '50.437000',
        'lng': '30.516000',
        'working_hours': 'Вт–Сб 12:00–20:00',
        'sort_order': 20,
    },
    {
        'name': 'Atelier Partner — Warszawa',
        'country': 'Польща',
        'city': 'Варшава',
        'address': 'ul. Mokotowska 19',
        'phone': '+48222000300',
        'email': 'warsaw@varvarova.com',
        'lat': '52.225000',
        'lng': '21.018000',
        'working_hours': 'Ср–Сб 12:00–18:00',
        'sort_order': 30,
    },
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
    settings.contacts_json = {
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
    settings.robots_txt = 'User-agent: *\nAllow: /\n'
    settings.save()

    for slug, title, body in PAGES:
        Page.objects.update_or_create(
            slug=slug,
            defaults={'title': title, 'body': body, 'is_published': True, 'seo_title': f'{title} — Varvarova'},
        )

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
            post.cover_image.save(
                f'{slug}.jpg',
                as_file(render_cover(title, tone), f'{slug}.jpg'),
                save=True,
            )

    banner, _banner_created = Banner.objects.update_or_create(
        sort_order=0,
        defaults={'title': 'Нова колекція', 'link_url': '/katalog/wedding/', 'is_active': True},
    )
    if banner.image:
        banner.image.delete(save=False)
    banner.image.save('hero.jpg', as_file(render_banner(), 'hero.jpg'), save=True)

    for row in SALONS:
        Salon.objects.update_or_create(
            name=row['name'],
            city=row['city'],
            defaults={**{k: v for k, v in row.items() if k not in ('name', 'city')}, 'is_active': True},
        )

    TrunkShow.objects.update_or_create(
        title='Trunk Show — Milano',
        defaults={
            'city': 'Мілан',
            'place': 'Brera Atelier',
            'starts_at': now + timedelta(days=21),
            'ends_at': now + timedelta(days=23),
            'description': 'Показ весільної лінії та couture для партнерів Італії.',
            'is_published': True,
        },
    )
    TrunkShow.objects.update_or_create(
        title='Trunk Show — Paris',
        defaults={
            'city': 'Париж',
            'place': 'Rue de Turenne',
            'starts_at': now + timedelta(days=45),
            'ends_at': now + timedelta(days=47),
            'description': 'Примірка нової колекції для салонів Франції.',
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
            item.image.save(
                f'bride-{slug}.jpg',
                as_file(render_cover(product.name, 'ivory'), f'bride-{slug}.jpg'),
                save=True,
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
