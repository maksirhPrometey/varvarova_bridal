from django.core.management.base import BaseCommand
from django.db import transaction

from src.core.seed import seed_accounts, seed_catalog, seed_content


class Command(BaseCommand):
    help = 'Ідемпотентні демо-дані вітрини Varvarova (каталог, контент, акаунти).'

    def handle(self, *args, **options):
        with transaction.atomic():
            catalog = seed_catalog()
            content = seed_content()
            accounts = seed_accounts()

        self.stdout.write(self.style.SUCCESS('seed_demo готово'))
        self.stdout.write(
            f"Категорії: {catalog['categories']}, товари: {catalog['products']} "
            f"(нових: {catalog['products_created']})"
        )
        self.stdout.write(
            f"Сторінки: {content['pages']}, FAQ: {content['faq']}, салони: {content['salons']}"
        )
        self.stdout.write(f"Адмін: {accounts['admin_email']} / {accounts['admin_password']}")
        self.stdout.write(f"Клієнт: {accounts['customer_email']} / {accounts['customer_password']}")
