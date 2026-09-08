# Бізнес-логіка — Varvarova

**Версія:** 1.0 · **Дата:** 2026-09-02  
**Стек:** Django 5+ · HTMX · Variant B  
**Skill:** `ecommerce_business_logic_skill`  
**Джерела:** `docs/sitemap.md`, `docs/oksana-mukha-website-overview.md`, `docs/tables.md` v1.1, моделі `src/*/models.py`, відповіді клієнта 2026-09-02

Це регламент для реалізації (selectors / services / views). Не UI (`shop_design`), не схема.

## Lock

| Тема | Рішення |
|---|---|
| Apps | `catalog` → `authentication` → `commerce` → `content`. Без `pricing` / `shipping` / `seo` app |
| Ціна | Одна `Product.price_uah`. Snapshot лише в `OrderItem` на `place_order`. `CartItem` без ціни (SEC-06) |
| Варіанти | Немає SKU-варіантів |
| Guest cart | Кошик по `session_key`; після логіну **merge** (сума `qty`, cap залишком) |
| Guest wishlist | `localStorage['varvarova_wishlist']` → POST `/wishlist/merge/` після логіну (`guest_wishlist_merge_skill`) |
| Guest checkout | `Order.user_id` NULL; thanks лише через `session['last_order_id']` + `number`, не голий pk (SEC-01) |
| НП | Snapshot на Order; **без ТТН** у MVP. Довідник: stub/fixture, доки немає live-клієнта |
| Салон | Самовивіз: snapshot name/address з активного `Salon`, не FK |
| Доставка грн | `shipping_uah = 0`, доки клієнт не дасть тарифи |
| Оплата | Enum у коді: `liqpay` \| `bank`. TX-лог — backlog M3 |
| Відгуки | Лише опубліковані з адмінки. Публічної форми створення немає (sitemap не вимагає) |
| Мова | Лише UK |
| Не в MVP | CRM, 1С, feeds, Checkbox, dual price, `*_uk`/`*_ru`, Attribute↔Category таблиця |

## Шари

| Файл | Дозволено | Заборонено |
|---|---|---|
| `selectors.py` | queryset, prefetch, фільтри, SEO-поля | `save` / `create` / `update` |
| `services.py` | мутації, `@transaction.atomic`, RBAC, винятки | рендер, читання POST напряму |
| `views.py` | parse → selector/service → render / JSON | бізнес-правила, ціна з форми |
| `urls.py` | маршрути нижче | — |

Винятки: `CartError`, `CheckoutError`, `OrderStatusError`, `WishlistError`, `AuthError`.

Контекст вітрини: лише публічні поля товару (`name`, `slug`, `price_uah`, `stock_qty`, опис, фото). Не віддавати службове.

Singleton: завжди `SiteSettings.load()`, ніколи `.first()`.

---

## Мапа: карта сайту → URL → controller

URL фіксуємо тут: у `sitemap.md` немає шляхів, лише розділи.

| Карта | URL | App.View | Дія |
|---|---|---|---|
| 1. Головна | `/` | `content.HomeView` | selector: банери `is_active`, `Product.is_featured`, trunk-show `is_published` (`starts_at` ≥ зараз першими), кореневі категорії |
| 2. Весільні — список | `/katalog/<slug>/` | `catalog.CatalogListView` | дерево від категорії `wedding` (і піткатегорії); HTMX partial сітки |
| 2. Вечірні — список | `/katalog/<slug>/` | той самий | корінь `evening` (+ couture, дружки як діти) |
| 2. Аксесуари — список | `/katalog/<slug>/` | той самий | корінь `accessories` (+ фати, рукавички, кейпи, пояси, знімні) |
| 2. Білизна — список | `/katalog/<slug>/` | той самий | корінь `lingerie` (+ бюстгальтери, трусики, підвʼязки, панчохи, боді) |
| 2. Фільтри | query `?a=<attr_code>=<value_slug>` | `catalog.selectors.filter_catalog` | AND між атрибутами; OR всередині одного `code` |
| 2. PDP | `/suknya/<slug>/` | `catalog.ProductDetailView` | активний товар, галерея (`is_main` першим), атрибути, `price_uah`; кнопка кошика лише якщо `stock_qty > 0` |
| 3. Про нас | `/about/` | `content.PageView` | `content_page.slug=about`, `is_published` |
| 3. Наречені | `/narecheni/` | `content.BrideGalleryView` | `is_published`, sort, optional product |
| 3. Блог список | `/blog/` | `content.BlogListView` | `is_published`, `-published_at` |
| 3. Блог пост | `/blog/<slug>/` | `content.BlogDetailView` | published |
| 3. Відгуки | `/vidhuky/` | `content.ReviewListView` | `is_published`; product optional |
| 4. Салони | `/salony/` | `content.SalonListView` | `is_active`, lat/lng для карти |
| 5. Партнерство | `/partnership/` | `content.PartnershipView` | page `partnership` + POST → `submit_partner_application` |
| 6. FAQ | `/faq/` | `content.FaqView` | `is_published`, sort |
| 6. Контакти | `/contacts/` | `content.ContactsView` | page `contacts` + `SiteSettings.load().contacts_json` |
| 6. Оплата/доставка/повернення | `/delivery/` | `content.PageView` | slug `delivery` |
| 6. Догляд | `/care/` | `content.PageView` | slug `care` (не per-SKU) |
| 6. Оферта | `/offer/` | `content.PageView` | slug `offer` |
| 6. Політика | `/privacy/` | `content.PageView` | slug `privacy` |
| 7. Кабінет | `/kabinet/` | `authentication.AccountView` | login required; імʼя, телефон, зміна пароля |
| 7. Історія замовлень | `/kabinet/zamovlennya/` | `commerce.AccountOrderListView` | `Order.user=request.user` |
| 7. Деталь замовлення | `/kabinet/zamovlennya/<number>/` | `commerce.AccountOrderDetailView` | scope user **або** staff; не pk |
| 7. Wishlist | `/wishlist/` | `catalog.WishlistView` | auth: DB; guest: `?ids=` з localStorage |
| 7. Кошик | `/koshyk/` | `commerce.CartDetailView` | HTMX add/update/remove |
| Checkout GET/POST | `/checkout/` | `commerce.CheckoutView` | `place_order` |
| Thanks | `/checkout/dyakuyemo/` | `commerce.CheckoutThanksView` | session `last_order_id` + number |
| Login | `/login/` | `authentication.LoginView` | email; після успіху cart merge + wishlist merge |
| Register | `/register/` | `authentication.RegisterView` | те саме merge |
| Logout | `/logout/` | `authentication.LogoutView` | POST |
| Reset | `/password-reset/` | `authentication.PasswordResetView` | стандартний Django email |
| HTMX кошик | `/koshyk/add/`, `/koshyk/qty/`, `/koshyk/remove/` | `commerce.Cart*View` | POST CSRF |
| Wishlist toggle/merge | `/wishlist/toggle/`, `/wishlist/merge/` | `catalog.Wishlist*View` | auth JSON; guest toggle лише JS |
| НП autocomplete | `/api/np/cities/`, `/api/np/warehouses/` | `commerce.NpStubView` | fixture; live лише з реальним клієнтом |
| robots | `/robots.txt` | `content.RobotsView` | `SiteSettings.robots_txt` або дефолт |
| sitemap.xml | `/sitemap.xml` | `content.SitemapXmlView` | публічні URL; після вітрини |

Не окремі URL (навмисно): `/aktsiyi/` (немає в карті), PDP tabs override, care per SKU, кабінет-адресна книга.

Навігація: header — головна, весільні, вечірні, про нас, салони, блог; footer — FAQ, контакти, delivery/care/offer/privacy, партнерство, wishlist, кошик.

---

## Catalog

**Видимість:** `is_active=True`. Категорія: `is_active` + усі предки активні, інакше 404.

**Дерево:** товар у **одній** категорії (`category_id`). Список гілки = товари цієї категорії **і всіх нащадків**. Товар не буває в двох коренях (напр. і сукня, і аксесуар).

**Наявність:** `in_stock = stock_qty > 0`. PDP показуємо при `is_active` навіть якщо 0; `add_item` тоді `CartError`.

**Бестселери:** `is_featured` + `is_active`, `sort_order`, ліміт на головній (напр. 8).

**Фільтри без Attribute↔Category:** у сайдбарі лише атрибути, для яких у поточному queryset є хоча б одне `ProductAttributeValue`. Коди з схеми: весільні `silhouette|color|fabric|decor`; вечірні `style|neckline|length`. Не показувати порожні.

**Сортування (enum у коді):** `new` (`-created_at`), `price_asc`, `price_desc`, `manual` (`sort_order`).

**Селектори:** `active_products()`, `category_by_slug()`, `filter_catalog(...)`, `product_by_slug()`, `featured_products()`, `wishlist_products_for_user()`, `active_products_by_ids(ids)`.

**Фото:** головне `is_main=True`, інакше перше за `sort_order`.

---

## Wishlist

| Хто | Джерело | Toggle |
|---|---|---|
| Guest | `localStorage['varvarova_wishlist']` = `[id, …]` | лише клієнт, без фейкового API |
| Auth | `WishlistItem` UNIQUE(user, product) | POST JSON, CSRF |

Після login/register **один** `merge_ids_for_user`: тільки `is_active` Product, невідомі id ігнорувати, потім clear localStorage. Лічильник хедера: одне джерело після hydrate.

Не плутати з merge кошика.

---

## Auth / кабінет

- Логін: email (lowercase) + пароль. `role` за замовчуванням `customer`.
- Реєстрація: email, пароль, імʼя; опційно телефон.
- Кабінет: `first_name`, `last_name`, `phone`, зміна пароля. Без збережених НП-адрес (немає полів у User).
- Замовлення кабінету: лише `user=request.user`. Staff/manager — адмінка Unfold, не чужі pk на вітрині.
- Після логіну порядок: `merge_guest_cart` → відповідь HTML → JS `wishlist/merge`.

RBAC вітрини: `customer` / анонім — свої кошик і замовлення. `manager` / `admin` / `is_superuser` — зміна статусу **через service** `change_order_status` (адмін-action теж викликає його). Окремої `manager_permission` немає: manager = `is_staff` + `role=manager`.

---

## Commerce — кошик

`get_active_cart(request)`:

- auth → один `Cart` `status=active` на user;
- guest → `session_key` (гарантувати `session.save()` до ключа);
- інваріант: `user` XOR `session_key` непорожній.

`add_item` / `update_qty` / `remove_item`:

- товар `is_active`;
- `qty >= 1`; підсумок по рядку ≤ `stock_qty`;
- UNIQUE (cart, product) → збільшити qty, не другий рядок;
- ціну не писати в кошик.

`merge_guest_cart(user, session_key)`: позиції session-cart у user-cart, qty = min(сума, stock); session-cart → `converted` або порожній abandoned.

Порожній кошик на checkout → редірект `/koshyk/`.

---

## Commerce — `place_order`

`@transaction.atomic`. Не довіряти ціні/сумі з POST.

1. Активний кошик + `select_for_update` на `Product` позицій.
2. Кожен рядок: товар активний, `stock_qty >= qty`, `unit = product.price_uah`, `line = unit * qty`.
3. Доставка: `shipping_uah = 0` (поки немає тарифів).
4. `total = subtotal + shipping`.
5. Валідація методу:
   - `np_warehouse` — обовʼязкові city/warehouse ref **і** name;
   - `np_courier` — city + `shipping_address`;
   - `pickup_salon` — салон `is_active`; у замовлення **копія** name/address (не id).
6. `number` унікальний (`VV-YYYYMMDD-NNNN`).
7. `Order` + `OrderItem` snapshot (`sku`, `name`, `unit_price_uah`).
8. Склад: `Product.objects.filter(pk=…, stock_qty__gte=qty).update(stock_qty=F('stock_qty')-qty)`; 0 рядків → `CheckoutError` (ERR-BIZ-05).
9. Кошик `status=converted`.
10. `OrderStatusLog`: `None → new`.
11. Оплата:
    - `liqpay` → `status=awaiting_payment`, `payment_status=pending`; редірект на оплату (сервіс LiqPay, ключі в `.env`);
    - `bank` → `new` або `awaiting_payment`, pending; реквізити з `contacts_json`.
12. Session: `last_order_id`, `last_order_number`. Лист клієнту — якщо є email backend.

Webhook LiqPay (окремий view, CSRF exempt, **перевірка signature** SEC-07): лише тоді `payment_status=paid`, `paid_at=now`, перехід `awaiting_payment → paid` через `change_order_status`. Ідемпотентність по `order.number`. Немає TX-таблиці в MVP.

---

## Статуси замовлення

```text
new ──────────────► awaiting_payment ──────► paid ──────► processing ──────► shipped ──────► done
  │                      │                    │              │
  └──────────────────────┴────────────────────┴──────────────┴──► cancelled
```

`ALLOWED_TRANSITIONS`:

| З | До |
|---|---|
| `new` | `awaiting_payment`, `cancelled` |
| `awaiting_payment` | `paid`, `cancelled` |
| `paid` | `processing`, `cancelled` |
| `processing` | `shipped`, `cancelled` |
| `shipped` | `done` |
| `done` / `cancelled` | — |

Інший стрибок → `OrderStatusError` (ERR-BIZ-08). Скасування після `paid`: `payment_status` не чіпати автоматично (refund — руками / backlog). Повернення складу при `cancelled` з `paid`/`processing` — **так**, `F('stock_qty')+qty` лише якщо ще не `shipped`/`done` (відвантажене не повертати без окремого рішення).

`change_order_status(order, to, *, user=None, note='')`: RBAC усередині (`admin` / `superuser` / `manager`+`is_staff`); писати `OrderStatusLog`.

---

## НП (MVP)

Фаза 0.5 `novaposhta_skill`: autocomplete з fixture. `place_order` **не** створює ТТН. Якщо зʼявиться `NP_API_KEY` без live-клієнта — не маскувати stub під live.

---

## Content / партнерка

| Сутність | Публічне правило |
|---|---|
| Banner | `is_active`, `sort_order` |
| TrunkShow | `is_published`; сортування `-starts_at` |
| Page | `is_published`; 404 якщо ні |
| FAQ / Review / Bride | `is_published` |
| Salon | `is_active` |
| Blog | `is_published` і `published_at` не в майбутньому |
| PartnerApplication | POST: honeypot/rate-limit; `status=new`; без авто-логіну |

`contacts_json`: телефони, email, соцмережі, реквізити `bank` — контракт ключів зафіксувати в `SiteSettings` help/адмінці при реалізації.

---

## Security (архітектура)

| SEC | Правило тут |
|---|---|
| 01 | Замовлення: `number` + user/session, не `get(pk=)` |
| 02 | Ціна лише з `Product` у `place_order` |
| 03 | Склад через `F()` + умову `stock_qty__gte` |
| 04 | Відгуки з адмінки; `|escape` у шаблоні; без `|safe` на user HTML |
| 05 | Upload лише ImageField + Pillow; media без execute |
| 06 | Кошик = product + qty |
| 07 | LiqPay webhook: signature |
| 08 | DEBUG/секрети — settings (вже) |
| 09 | Не застосовно (немає cost/синку) |

---

## Ланцюжок реалізації

```
1. content selectors + Home + Page/FAQ/Blog/Reviews/Salons/Brides
2. catalog list + PDP + фільтри
3. authentication (login/register/reset/kabinet профіль)
4. commerce cart + merge
5. wishlist toggle/merge
6. checkout + place_order + thanks
7. NP stub autocomplete
8. LiqPay slot (можна bank-only до ключів)
9. account orders + change_order_status
10. partner POST
11. robots + sitemap.xml
```

Jobs (abandoned cart) — не MVP.

---

## Verify: карта → цей документ → код

Колонка «код» оновлюється, коли зʼявляться urls/views.

| Рядок карти | Спека | Код |
|---|---|---|
| 1. Банери / бестселери / trunk-show / категорії | ✅ HomeView | ✅ |
| 2. Каталоги весільні/вечірні + фільтри | ✅ CatalogListView | ✅ |
| 2. PDP фото/опис/ціна/кошик | ✅ ProductDetail + add_item | ✅ PDP (кнопка без POST) |
| 3. Про нас | ✅ `/about/` | ✅ |
| 3. Наречені | ✅ `/narecheni/` | ✅ |
| 3. Блог | ✅ `/blog/`, `/blog/<slug>/` | ✅ |
| 3. Відгуки | ✅ `/vidhuky/` (без UGC) | ✅ |
| 4. Салони | ✅ `/salony/` | ✅ |
| 5. Партнерство + заявка | ✅ `/partnership/` | ✅ GET (POST — крок 10) |
| 6. FAQ | ✅ `/faq/` | ✅ |
| 6. Контакти | ✅ `/contacts/` + settings | ✅ |
| 6. Доставка / догляд / оферта / privacy | ✅ page slugs | ✅ |
| 7. Кабінет / історія | ✅ `/kabinet/` | ❌ |
| 7. Wishlist | ✅ DB + localStorage merge | ❌ |
| 7. Кошик + checkout + оплата | ✅ place_order | ❌ |
| Guest checkout | ✅ user NULL + session thanks | ❌ |
| CRM / 1С / feeds / Checkbox | поза MVP (lock) | — |
| PDP tab / care per SKU | N/A | — |

Будь-який новий рядок карти без рядка тут = ERR-BIZ-01.
