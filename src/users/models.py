from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models

from src.core.models import TimeStampedModel


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('role', User.Role.CUSTOMER)
        if not email:
            raise ValueError('Email обовʼязковий.')
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', User.Role.ADMIN)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Суперкористувач має мати is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Суперкористувач має мати is_superuser=True.')
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser, TimeStampedModel):
    class Role(models.TextChoices):
        ADMIN = 'admin', 'Адмін'
        MANAGER = 'manager', 'Менеджер'
        CUSTOMER = 'customer', 'Клієнт'

    username = None
    email = models.EmailField('Email', unique=True)
    phone = models.CharField('Телефон', max_length=32, null=True, blank=True)
    role = models.CharField(
        'Роль',
        max_length=16,
        choices=Role.choices,
        default=Role.CUSTOMER,
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS: list[str] = []
    objects = UserManager()

    class Meta(AbstractUser.Meta):
        abstract = False
        db_table = 'users_user'
        verbose_name = 'Користувач'
        verbose_name_plural = 'Користувачі'

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.email
