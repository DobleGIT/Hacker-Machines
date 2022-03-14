from django.apps import AppConfig


class AccountsConfig(AppConfig):
    name = 'accounts'

    def ready(self): #esto lo hacemos para que funcionen las señales 
        import accounts.signals 