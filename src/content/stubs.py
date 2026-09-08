from types import SimpleNamespace

PAGE_STUBS = {
    'about': SimpleNamespace(
        slug='about',
        title='Про бренд',
        body=(
            '<p>Світ Varvarova. Текст сторінки зʼявиться після публікації '
            'в адмінці (Content → Сторінки, slug <code>about</code>).</p>'
        ),
        seo_title='',
    ),
    'delivery': SimpleNamespace(
        slug='delivery',
        title='Доставка та оплата',
        body=(
            '<p>Умови доставки, оплати та повернення. '
            'Заглушка — опублікуйте сторінку <code>delivery</code> в адмінці.</p>'
        ),
        seo_title='',
    ),
    'care': SimpleNamespace(
        slug='care',
        title='Догляд за сукнею',
        body=(
            '<p>Рекомендації з догляду. '
            'Заглушка — опублікуйте сторінку <code>care</code> в адмінці.</p>'
        ),
        seo_title='',
    ),
    'offer': SimpleNamespace(
        slug='offer',
        title='Публічна оферта',
        body=(
            '<p>Текст оферти. '
            'Заглушка — опублікуйте сторінку <code>offer</code> в адмінці.</p>'
        ),
        seo_title='',
    ),
    'privacy': SimpleNamespace(
        slug='privacy',
        title='Політика конфіденційності',
        body=(
            '<p>Політика конфіденційності. '
            'Заглушка — опублікуйте сторінку <code>privacy</code> в адмінці.</p>'
        ),
        seo_title='',
    ),
}

PARTNERSHIP_STUB = SimpleNamespace(
    slug='partnership',
    title='Стати партнером',
    body=(
        '<p>Понад 400 салонів у 38 країнах працюють з Varvarova напряму '
        'з виробництва у Львові. Повний текст — після публікації сторінки '
        '<code>partnership</code> в адмінці.</p>'
    ),
    seo_title='',
)

CATEGORY_STUBS = {
    'wedding': SimpleNamespace(
        slug='wedding',
        name='Весільні сукні',
        description=(
            '<p>Колекція весільних суконь. '
            'Створіть категорію зі slug <code>wedding</code> в адмінці Catalog.</p>'
        ),
        seo_title='',
    ),
    'evening': SimpleNamespace(
        slug='evening',
        name='Вечірні сукні',
        description=(
            '<p>Колекція вечірніх суконь. '
            'Створіть категорію зі slug <code>evening</code> в адмінці Catalog.</p>'
        ),
        seo_title='',
    ),
}


def page_stub(slug: str):
    return PAGE_STUBS.get(slug)


def category_stub(slug: str):
    return CATEGORY_STUBS.get(slug)
