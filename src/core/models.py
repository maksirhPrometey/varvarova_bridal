from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField('Створено', auto_now_add=True)
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        abstract = True


class CreatedAtModel(models.Model):
    created_at = models.DateTimeField('Створено', auto_now_add=True)

    class Meta:
        abstract = True


class UpdatedAtModel(models.Model):
    updated_at = models.DateTimeField('Оновлено', auto_now=True)

    class Meta:
        abstract = True


class SeoFieldsMixin(models.Model):
    """SEO override на сутності — без окремої polymorphic-таблиці."""

    seo_title = models.CharField('SEO title', max_length=512, null=True, blank=True)
    seo_description = models.TextField('SEO description', null=True, blank=True)
    seo_keywords = models.CharField('SEO keywords', max_length=512, null=True, blank=True)

    class Meta:
        abstract = True
