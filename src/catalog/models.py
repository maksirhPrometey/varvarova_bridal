from django.db import models
from django.db.models import Q

from src.core.models import CreatedAtModel, SeoFieldsMixin, TimeStampedModel


class Category(SeoFieldsMixin, TimeStampedModel):
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
        verbose_name='Батьківська категорія',
    )
    name = models.CharField('Назва', max_length=255)
    slug = models.SlugField('Slug', max_length=255, unique=True)
    description = models.TextField('Опис', null=True, blank=True)
    sort_order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активна', default=True)

    class Meta:
        db_table = 'catalog_category'
        verbose_name = 'Категорія'
        verbose_name_plural = 'Категорії'
        indexes = [
            models.Index(fields=['parent', 'sort_order'], name='catalog_category_parent_sort'),
        ]

    def __str__(self) -> str:
        return self.name


class Attribute(models.Model):
    code = models.CharField('Код', max_length=64, unique=True)
    name = models.CharField('Назва', max_length=128)
    filterable = models.BooleanField('Фільтр', default=True)
    sort_order = models.IntegerField('Порядок', default=0)

    class Meta:
        db_table = 'catalog_attribute'
        verbose_name = 'Атрибут'
        verbose_name_plural = 'Атрибути'
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.name


class AttributeValue(models.Model):
    attribute = models.ForeignKey(
        Attribute,
        on_delete=models.CASCADE,
        related_name='values',
        verbose_name='Атрибут',
    )
    value = models.CharField('Значення', max_length=128)
    slug = models.SlugField('Slug', max_length=128)
    sort_order = models.IntegerField('Порядок', default=0)

    class Meta:
        db_table = 'catalog_attribute_value'
        verbose_name = 'Значення атрибута'
        verbose_name_plural = 'Значення атрибутів'
        constraints = [
            models.UniqueConstraint(
                fields=['attribute', 'slug'],
                name='catalog_attr_value_attr_slug_uniq',
            ),
        ]
        ordering = ['sort_order', 'id']

    def __str__(self) -> str:
        return self.value


class Product(SeoFieldsMixin, TimeStampedModel):
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Категорія',
    )
    sku = models.CharField('SKU', max_length=64, unique=True)
    slug = models.SlugField('Slug', max_length=255, unique=True)
    name = models.CharField('Назва', max_length=255)
    short_description = models.CharField(
        'Короткий опис',
        max_length=512,
        null=True,
        blank=True,
    )
    description = models.TextField('Опис', null=True, blank=True)
    price_uah = models.DecimalField('Ціна, грн', max_digits=12, decimal_places=2)
    stock_qty = models.PositiveIntegerField('Залишок', default=0)
    is_active = models.BooleanField('Активний', default=True)
    is_featured = models.BooleanField('Бестселер', default=False)
    sort_order = models.IntegerField('Порядок', default=0)

    class Meta:
        db_table = 'catalog_product'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товари'
        indexes = [
            models.Index(fields=['is_active'], name='catalog_product_is_active'),
            models.Index(fields=['is_featured'], name='catalog_product_is_featured'),
            models.Index(fields=['price_uah'], name='catalog_product_price_uah'),
        ]
        constraints = [
            models.CheckConstraint(
                condition=Q(price_uah__gte=0),
                name='catalog_product_price_uah_gte_0',
            ),
            models.CheckConstraint(
                condition=Q(stock_qty__gte=0),
                name='catalog_product_stock_qty_gte_0',
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def in_stock(self) -> bool:
        return self.stock_qty > 0

    def get_main_image(self):
        images = list(self.images.all())
        for image in images:
            if image.is_main:
                return image
        return images[0] if images else None


class ProductAttributeValue(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='attribute_values',
        verbose_name='Товар',
    )
    attribute_value = models.ForeignKey(
        AttributeValue,
        on_delete=models.CASCADE,
        related_name='product_links',
        verbose_name='Значення атрибута',
    )

    class Meta:
        db_table = 'catalog_product_attribute_value'
        verbose_name = 'Атрибут товару'
        verbose_name_plural = 'Атрибути товарів'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'attribute_value'],
                name='catalog_pav_product_value_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.product_id}:{self.attribute_value_id}'


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name='Товар',
    )
    image = models.ImageField('Зображення', upload_to='products/%Y/%m/', max_length=255)
    alt = models.CharField('Alt', max_length=255, null=True, blank=True)
    sort_order = models.IntegerField('Порядок', default=0)
    is_main = models.BooleanField('Головне', default=False)

    class Meta:
        db_table = 'catalog_product_image'
        verbose_name = 'Фото товару'
        verbose_name_plural = 'Фото товарів'
        ordering = ['sort_order', 'id']
        constraints = [
            models.UniqueConstraint(
                fields=['product'],
                condition=Q(is_main=True),
                name='catalog_product_image_one_main',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.product_id}:{self.sort_order}'


class WishlistItem(CreatedAtModel):
    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name='Користувач',
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='wishlist_items',
        verbose_name='Товар',
    )

    class Meta:
        db_table = 'catalog_wishlist_item'
        verbose_name = 'Обране'
        verbose_name_plural = 'Обране'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='catalog_wishlist_user_product_uniq',
            ),
        ]

    def __str__(self) -> str:
        return f'{self.user_id}:{self.product_id}'
