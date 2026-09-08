# Схема БД — Varvarova (bridal)

**Версія:** 1.1 · **Дата:** 2026-09-02  
**Стек:** Django 5+ · PostgreSQL · `ecommerce_db_schema_skill`  
**Варіант apps:** **B** (тонке ядро)  
**Мова контенту:** лише UK  
**Джерела:** `docs/sitemap.md`, `docs/oksana-mukha-website-overview.md`, відповіді клієнта 2026-09-02  
**v1.1:** спрощення 1–9 (FK категорії, без PDP-tab/care/crm/css-vars, snapshot салону, тонший banner/image)

## Рішення (lock)

| Питання | Рішення |
|---|---|
| Продажі | Повний e-commerce: кошик → checkout → оплата → доставка |
| Apps | Variant B: без `pricing`, без `shipping`, без окремого `seo` |
| Ціна | Одна `price_uah` на `Product` |
| Варіанти | Немає SKU-варіантів — один рядок = один товар |
| Салони | Лише довідник адрес |
| Guest | Кошик/checkout без акаунта; wishlist гостя — `localStorage` |
| Не в MVP (lock) | CRM, 1С, feeds, Checkbox — лише backlog |

## Apps

| App | Моделі | Примітка |
|---|---|---|
| `core` | — | `TimeStampedModel`, `SeoFieldsMixin` (не BC) |
| `users` | `User` | `AUTH_USER_MODEL` |
| `authentication` | — | login / register / reset — без таблиць |
| `catalog` | товар, категорії, атрибути, галерея, wishlist (auth) | |
| `commerce` | cart, order, status log | НП + salon snapshot на `Order` |
| `content` | settings, pages, FAQ, blog, reviews, salons, banners, trunk-show, brides, partner lead | |

---

## ER (ядро)

```text
User 1──* Order (nullable user = guest)
User 1──* Cart
User 1──* WishlistItem *──1 Product

Category 1──* Product
Attribute → AttributeValue → ProductAttributeValue ← Product
Product 1──* ProductImage

Cart 1──* CartItem *──1 Product
Order 1──* OrderItem
Order 1──* OrderStatusLog
```

---

## 1. `users`

### `users_user` (`AUTH_USER_MODEL`)

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| email | CITEXT UNIQUE | | логін |
| password | varchar | | |
| first_name | varchar(150) | | |
| last_name | varchar(150) | | |
| phone | varchar(32) | ✓ | |
| role | varchar(16) | | `admin` \| `manager` \| `customer` (default `customer`) |
| is_active | bool | | |
| is_staff | bool | | |
| date_joined | timestamptz | | |
| created_at / updated_at | timestamptz | | mixin |

Індекс: `email`. Без MTI (ERR-SCHEMA-03). Без окремого `customer_profile`.

---

## 2. `catalog`

### `catalog_category`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| parent_id | FK → category | ✓ | Весільні / Вечірні → піткатегорії |
| name | varchar(255) | | |
| slug | varchar(255) UNIQUE | | |
| description | text | ✓ | |
| sort_order | int | | default 0 |
| is_active | bool | | |
| seo_title / seo_description / seo_keywords | | ✓ | mixin |
| created_at / updated_at | | | mixin |

Індекси: `(parent_id, sort_order)`, `slug`.

**Дерево (контент):** `wedding` · `evening` · `accessories` · `lingerie` (+ піткатегорії: силуети / couture·дружки / фати·рукавички·кейпи·пояси·знімні / бюстгальтери·трусики·підвʼязки·панчохи·боді).

### `catalog_attribute`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| code | varchar(64) UNIQUE | | `silhouette`, `color`, `fabric`, `decor`, `style`, `neckline`, `length` |
| name | varchar(128) | | |
| filterable | bool | | default true |
| sort_order | int | | |

### `catalog_attribute_value`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| attribute_id | FK | | |
| value | varchar(128) | | |
| slug | varchar(128) | | |
| sort_order | int | | |

UNIQUE `(attribute_id, slug)`.

### `catalog_product`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| category_id | FK → category | | одна категорія (лист або гілка) |
| sku | varchar(64) UNIQUE | | |
| slug | varchar(255) UNIQUE | | |
| name | varchar(255) | | |
| short_description | varchar(512) | ✓ | картка каталогу |
| description | text | ✓ | PDP |
| price_uah | numeric(12,2) | | єдина вітрина ціна |
| stock_qty | int | | ≥0; наявність = `stock_qty > 0` |
| is_active | bool | | |
| is_featured | bool | | бестселери на головній |
| sort_order | int | | |
| seo_* | mixin | ✓ | |
| created_at / updated_at | | | |

Індекси: `category_id`, `is_active`, `is_featured`, `price_uah`.

**Немає:** M2M categories, Brand, Supplier, Variant, `care_notes`, `tab_order_override`, `pricing_*`.

### `catalog_product_attribute_value`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| product_id | FK | | |
| attribute_value_id | FK | | |

UNIQUE `(product_id, attribute_value_id)`.

### `catalog_product_image`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| product_id | FK | | |
| image | varchar/path | | |
| alt | varchar(255) | ✓ | |
| sort_order | int | | |
| is_main | bool | | |

Partial UNIQUE: один `is_main=true` на `product_id`.

### `catalog_wishlist_item`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| user_id | FK → users_user | | лише auth |
| product_id | FK | | |
| created_at | timestamptz | | |

UNIQUE `(user_id, product_id)`. Guest: `localStorage` + merge після логіну.

---

## 3. `commerce`

### `commerce_cart`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| user_id | FK | ✓ | null = гість |
| session_key | varchar(40) | ✓ | |
| status | varchar(16) | | `active` \| `converted` \| `abandoned` |
| created_at / updated_at | | | |

Індекси: `(session_key, status)`, `(user_id, status)`. Один `active` на user / session.

### `commerce_cart_item`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| cart_id | FK | | |
| product_id | FK | | |
| qty | int | | default 1, ≥1 |
| created_at / updated_at | | | |

UNIQUE `(cart_id, product_id)`. Без `unit_price` (SEC-06) — ціна з Product до order.

### `commerce_order`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| number | varchar(32) UNIQUE | | |
| user_id | FK | ✓ | null = guest |
| status | varchar(32) | | `new` \| `awaiting_payment` \| `paid` \| `processing` \| `shipped` \| `done` \| `cancelled` |
| customer_name | varchar(255) | | snapshot |
| customer_email | varchar(254) | | |
| customer_phone | varchar(32) | | |
| comment | text | ✓ | |
| subtotal_uah | numeric(12,2) | | |
| shipping_uah | numeric(12,2) | | default 0 |
| total_uah | numeric(12,2) | | |
| payment_method | varchar(32) | | enum у коді |
| payment_status | varchar(32) | | `pending` \| `paid` \| `failed` \| `refunded` |
| paid_at | timestamptz | ✓ | |
| shipping_method | varchar(32) | | `np_warehouse` \| `np_courier` \| `pickup_salon` \| … |
| np_city_ref | varchar(64) | ✓ | |
| np_city_name | varchar(255) | ✓ | |
| np_warehouse_ref | varchar(64) | ✓ | |
| np_warehouse_name | varchar(255) | ✓ | |
| shipping_address | text | ✓ | кур’єр / інше |
| pickup_salon_name | varchar(255) | ✓ | snapshot (не FK) |
| pickup_salon_address | varchar(512) | ✓ | snapshot |
| created_at / updated_at | | | |

Індекси: `status`, `payment_status`, `customer_email`, `created_at`.

### `commerce_order_item`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| order_id | FK | | |
| product_id | FK | ✓ | SET NULL якщо товар видалили |
| sku_snapshot | varchar(64) | | |
| name_snapshot | varchar(255) | | |
| unit_price_uah | numeric(12,2) | | snapshot на create_order |
| qty | int | | |
| line_total_uah | numeric(12,2) | | |

### `commerce_order_status_log`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| order_id | FK | | |
| from_status | varchar(32) | ✓ | |
| to_status | varchar(32) | | |
| note | text | ✓ | |
| actor_id | FK → users_user | ✓ | |
| created_at | timestamptz | | |

---

## 4. `content`

### `content_site_settings` (singleton)

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | один рядок |
| site_name | varchar(255) | | |
| logo | path | ✓ | |
| contacts_json | jsonb | | телефони, email, соцмережі |
| robots_txt | text | ✓ | |
| updated_at | | | |

### `content_page`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| slug | varchar(128) UNIQUE | | `about`, `delivery`, `care`, `offer`, `privacy`, `contacts`, `partnership` |
| title | varchar(255) | | |
| body | text | | |
| is_published | bool | | |
| seo_* | mixin | ✓ | |
| updated_at | | | |

### `content_faq_item`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| question | varchar(512) | | |
| answer | text | | |
| sort_order | int | | |
| is_published | bool | | |

### `content_blog_post`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| slug | varchar(255) UNIQUE | | |
| title | varchar(255) | | |
| excerpt | varchar(512) | ✓ | |
| body | text | | |
| cover_image | path | ✓ | |
| published_at | timestamptz | ✓ | |
| is_published | bool | | |
| seo_* | mixin | ✓ | |
| created_at / updated_at | | | |

### `content_review`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| author_name | varchar(255) | | |
| text | text | | |
| rating | smallint | ✓ | 1–5 |
| product_id | FK | ✓ | |
| is_published | bool | | |
| sort_order | int | | |
| created_at | | | |

### `content_salon`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| name | varchar(255) | | |
| country | varchar(128) | ✓ | |
| city | varchar(128) | | |
| address | varchar(512) | | |
| phone | varchar(64) | ✓ | |
| email | varchar(254) | ✓ | |
| lat / lng | numeric(9,6) | ✓ | |
| working_hours | varchar(255) | ✓ | |
| sort_order | int | | |
| is_active | bool | | |

### `content_banner`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| title | varchar(255) | ✓ | |
| image | path | | |
| link_url | varchar(512) | ✓ | |
| sort_order | int | | |
| is_active | bool | | |

### `content_trunk_show`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| title | varchar(255) | | |
| city | varchar(128) | ✓ | |
| place | varchar(255) | ✓ | |
| starts_at | timestamptz | | |
| ends_at | timestamptz | ✓ | |
| description | text | ✓ | |
| is_published | bool | | |

### `content_bride_gallery_item`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| title | varchar(255) | ✓ | |
| image | path | | |
| product_id | FK | ✓ | |
| sort_order | int | | |
| is_published | bool | | |

### `content_partner_application`

| Поле | Тип | Null | Опис |
|---|---|---|---|
| id | PK | | |
| company_name | varchar(255) | | |
| contact_name | varchar(255) | | |
| email | varchar(254) | | |
| phone | varchar(32) | | |
| city | varchar(128) | ✓ | |
| message | text | ✓ | |
| status | varchar(16) | | `new` \| `in_progress` \| `done` \| `rejected` |
| created_at | | | |

---

## Спрощення

| Прибрано / змінено | Чому |
|---|---|
| `pricing`, `shipping`, `seo` apps | Variant B |
| Brand, Supplier, Variant | монобренд, один товар |
| Product ↔ Category **M2M → FK** | одна категорія на сукню |
| `tab_order_override`, `pdp_tab_order` | вкладки PDP у шаблоні; карта без override |
| `care_notes` на Product | догляд = `content_page` slug=`care` |
| `crm_external_id` | CRM lock; додати поле пізніше |
| app `integrations` | не в MVP |
| `pickup_salon_id` FK → **name/address snapshot** | як НП-поля |
| `extra_css_vars` | токени в CSS |
| `ProductImage.title` | достатньо `alt` |
| Banner `starts_at/ends_at` | `is_active` + `sort_order` |
| Guest wishlist table | localStorage + merge |
| `is_in_stock` | лише `stock_qty` |

---

## Backlog (не мігрувати)

| Модуль | Lock | Нотатка |
|---|---|---|
| CRM sync | **lock** | за потреби — `crm_external_id` на Order |
| 1С / Unipro | **lock** | — |
| Product feeds | **lock** | — |
| Checkbox / ПРРО | **lock** | — |
| Payment TX log | M3 | `payment_status` / `paid_at` достатньо для MVP |
| TTN / multi-ФОП | M+ | → Variant A `shipping` |
| Attribute ↔ Category | optional | обмежити фільтри по дереву |
| `redirect_301` | optional | legacy URL |

---

## Verify: карта ↔ таблиці (після v1.1)

| Вимога sitemap | Покриття | Статус |
|---|---|---|
| 1. Банери | `content_banner` | ✅ |
| 1. Бестселери | `Product.is_featured` | ✅ |
| 1. Trunk-show | `content_trunk_show` | ✅ |
| 1. Категорії | `catalog_category` | ✅ |
| 2. Каталоги весільні/вечірні | `Product.category_id` + дерево | ✅ |
| 2. Фільтри | `attribute*` | ✅ |
| 2. PDP фото/опис/ціна/кошик | image + product + cart | ✅ |
| 3. Про нас | `content_page` `about` | ✅ |
| 3. Наречені | `content_bride_gallery_item` | ✅ |
| 3. Блог | `content_blog_post` | ✅ |
| 3. Відгуки | `content_review` | ✅ |
| 4. Салони | `content_salon` | ✅ |
| 5. Партнерство + заявка | page + `partner_application` | ✅ |
| 6. FAQ / контакти / доставка / догляд / юр. | `faq` + `page` + settings | ✅ |
| 7. Кабінет / wishlist / кошик | User + wishlist + cart/order | ✅ |
| Guest checkout | `Order.user_id` NULL | ✅ |
| CRM / 1С / feeds / Checkbox | backlog | ✅ lock |
| PDP tab override | — навмисно прибрано | ✅ N/A |
| Care per SKU | — глобальна сторінка `care` | ✅ |

## Verify: рішення клієнта

| Рішення | Статус |
|---|---|
| Повний e-commerce / Variant B / одна ціна / без варіантів | ✅ |
| Салон = довідник / UK / guest ok | ✅ |

---

## Перед Django

- [ ] `core.models`: `TimeStampedModel`, `SeoFieldsMixin`
- [ ] `AUTH_USER_MODEL = users.User`
- [ ] Далі: `django_models_from_schema_skill`

## Чеклист skill

- [x] Variant B зафіксовано
- [x] Без pricing; ціна на Product
- [x] Verify після simplify (v1.1)
- [x] Order: guest + NP/salon snapshot + status log
- [x] Lock CRM / 1С / feeds / Checkbox
