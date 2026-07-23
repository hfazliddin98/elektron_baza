from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'
    verbose_name = 'Foydalanuvchilar va ustalar'

    def ready(self):
        from . import signals  # noqa: F401
